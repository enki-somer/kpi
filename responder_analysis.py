#!/usr/bin/env python3
"""
WhatsApp Chat Parser and RESPONDER Response Time Analyzer
Measures how long each person takes to respond to others' messages.
"""

import re
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import List, Dict, Tuple, Optional
import numpy as np

class ResponderAnalysisParser:
    def __init__(self, chat_file_path: str):
        self.chat_file_path = chat_file_path
        self.messages = []
        self.conversation_threads = []
        self.responder_analysis = []
        
        # Conversation starter patterns (more comprehensive)
        self.conversation_starters = [
            # Greetings
            r'هلو\b', r'مرحبا\b', r'صباح\s*(الخير|النور)', r'مساء\s*(الخير|النور)',
            r'شلونكم\b', r'شلونك\b', r'اهلا\b', r'السلام\s*عليكم',
            r'hello\b', r'hi\b', r'good\s*morning', r'good\s*evening', r'how\s*are\s*you',
            
            # Questions and requests
            r'\?', r'ممكن', r'احتاج', r'نحتاج', r'شلون', r'وين', r'متى', r'ليش',
            r'can\s*you', r'could\s*you', r'please', r'need', r'help',
            
            # Technical/Work related starters
            r'تكت\b', r'ticket', r'مشكلة', r'problem', r'issue', r'error',
            r'سيرفر', r'server', r'نود', r'node', r'بورت', r'port',
            r'ترفك', r'traffic', r'سعة', r'capacity', r'سرعة', r'speed',
            
            # Urgent/Important markers
            r'عاجل', r'urgent', r'مهم', r'important', r'فوري', r'immediate',
            r'ايرجنت', r'emergency', r'مشكلة', r'problem',
            
            # Status updates
            r'تقرير', r'report', r'حالة', r'status', r'تحديث', r'update',
            r'مكتمل', r'completed', r'جاهز', r'ready', r'تم', r'done'
        ]
        
        # Compile regex patterns for efficiency
        self.conversation_regex = re.compile('|'.join(self.conversation_starters), re.IGNORECASE)
        
        # Configuration
        self.min_gap_hours = 4  # Only consider gaps > 4 hours as conversation breaks
        self.max_response_window_hours = 24  # Look for responses within 24 hours
        self.day_break_hours = 12  # Consider > 12 hours as potential day break
        
    def parse_chat_file(self) -> List[Dict]:
        """Parse the WhatsApp chat file and extract messages with metadata."""
        messages = []
        
        try:
            with open(self.chat_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(self.chat_file_path, 'r', encoding='latin-1') as file:
                lines = file.readlines()
        
        current_message = None
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts with date pattern (MM/DD/YY, HH:MM AM/PM)
            date_pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2})\s*(AM|PM)\s*-\s*(.+?):\s*(.*)$'
            match = re.match(date_pattern, line)
            
            if match:
                # Save previous message if exists
                if current_message:
                    messages.append(current_message)
                
                # Parse new message
                date_str, time_str, am_pm, sender, content = match.groups()
                
                # Parse datetime
                try:
                    # Handle different date formats and malformed dates
                    date_parts = date_str.split('/')
                    
                    # Fix malformed dates like "9/2019/2021" -> "9/19/2021"
                    if len(date_parts) == 3:
                        month, day, year = date_parts
                        
                        # Handle cases where day is actually year (like 9/2019/2021)
                        if len(day) == 4 and len(year) == 4:
                            # This is malformed, try to fix it
                            if int(day) > 12:  # day is actually year
                                day, year = year, day
                            else:
                                # Swap day and year
                                day, year = year, day
                        
                        # Ensure year is 4 digits
                        if len(year) == 2:
                            year = '20' + year
                        
                        # Ensure day is valid (1-31)
                        if int(day) > 31:
                            day = str(int(day) % 100)  # Take last 2 digits
                        
                        date_str = f"{month}/{day}/{year}"
                    
                    datetime_str = f"{date_str} {time_str} {am_pm}"
                    timestamp = datetime.strptime(datetime_str, "%m/%d/%Y %I:%M %p")
                    
                    current_message = {
                        'line_number': line_num + 1,
                        'timestamp': timestamp,
                        'sender': sender.strip(),
                        'content': content.strip(),
                        'full_content': content.strip(),
                        'is_conversation_starter': self.is_conversation_starter(content),
                        'message_length': len(content.strip()),
                        'message_type': self.classify_message_type(content)
                    }
                except ValueError as e:
                    print(f"Error parsing datetime on line {line_num + 1}: {e}")
                    continue
            else:
                # Continuation of previous message
                if current_message:
                    current_message['content'] += ' ' + line
                    current_message['full_content'] += ' ' + line
                    current_message['message_length'] = len(current_message['full_content'])
                    current_message['is_conversation_starter'] = self.is_conversation_starter(current_message['full_content'])
                    current_message['message_type'] = self.classify_message_type(current_message['full_content'])
        
        # Add the last message
        if current_message:
            messages.append(current_message)
        
        self.messages = messages
        return messages
    
    def is_conversation_starter(self, text: str) -> bool:
        """Check if a message is likely to start a new conversation."""
        return bool(self.conversation_regex.search(text))
    
    def classify_message_type(self, text: str) -> str:
        """Classify the type of message."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['تكت', 'ticket', 'مشكلة', 'problem']):
            return 'Technical Issue'
        elif any(word in text_lower for word in ['عاجل', 'urgent', 'ايرجنت', 'emergency']):
            return 'Urgent'
        elif any(word in text_lower for word in ['تقرير', 'report', 'حالة', 'status']):
            return 'Status Update'
        elif any(word in text_lower for word in ['هلو', 'مرحبا', 'hello', 'hi']):
            return 'Greeting'
        elif '?' in text or any(word in text_lower for word in ['ممكن', 'can you', 'could you']):
            return 'Question'
        else:
            return 'General'
    
    def detect_conversation_threads(self) -> List[Dict]:
        """Detect conversation threads using REALISTIC gap analysis."""
        if not self.messages:
            self.parse_chat_file()
        
        threads = []
        current_thread = None
        
        for i, message in enumerate(self.messages):
            # Check if this message starts a new conversation thread
            is_new_thread = False
            
            if current_thread is None:
                # First message or no active thread
                is_new_thread = True
            else:
                # Calculate time gap from last message in current thread
                time_gap = message['timestamp'] - current_thread['last_message_time']
                gap_hours = time_gap.total_seconds() / 3600
                
                # Only create new thread for VERY long gaps
                if gap_hours > self.min_gap_hours:
                    # Very long gap - definitely new conversation
                    is_new_thread = True
                elif gap_hours > self.day_break_hours:
                    # Day break - likely new conversation unless it's a continuation
                    if message['is_conversation_starter']:
                        is_new_thread = True
                    # Otherwise, continue the thread (might be overnight work)
                elif gap_hours > 2 and message['is_conversation_starter']:
                    # Moderate gap + conversation starter = new thread
                    is_new_thread = True
                # For gaps < 2 hours, always continue the thread
            
            if is_new_thread:
                # Start new thread
                if current_thread:
                    threads.append(current_thread)
                
                current_thread = {
                    'thread_id': len(threads) + 1,
                    'start_time': message['timestamp'],
                    'starter': message['sender'],
                    'starter_message': message['content'],
                    'message_type': message['message_type'],
                    'messages': [message],
                    'last_message_time': message['timestamp'],
                    'last_sender': message['sender'],
                    'participants': {message['sender']},
                    'total_gap_hours': 0
                }
            else:
                # Continue current thread
                current_thread['messages'].append(message)
                current_thread['last_message_time'] = message['timestamp']
                current_thread['last_sender'] = message['sender']
                current_thread['participants'].add(message['sender'])
                
                # Track total gap time in this thread
                if len(current_thread['messages']) > 1:
                    prev_message = current_thread['messages'][-2]
                    gap = message['timestamp'] - prev_message['timestamp']
                    current_thread['total_gap_hours'] += gap.total_seconds() / 3600
        
        # Add the last thread
        if current_thread:
            threads.append(current_thread)
        
        self.conversation_threads = threads
        return threads
    
    def analyze_responder_performance(self) -> List[Dict]:
        """Analyze how long each person takes to respond to others' messages."""
        if not self.messages:
            self.parse_chat_file()
        
        responder_stats = {}
        ignored_messages = []
        response_pairs = []
        
        # Go through each message and find responses
        for i, message in enumerate(self.messages):
            # Skip system messages
            if message['sender'] in ['Messages and calls are end-to-end encrypted', '']:
                continue
                
            # Look for the next message from a different sender
            response_found = False
            response_time_minutes = None
            responder = None
            
            for j in range(i + 1, min(i + 20, len(self.messages))):  # Look ahead max 20 messages
                next_message = self.messages[j]
                
                # Skip if same sender
                if next_message['sender'] == message['sender']:
                    continue
                
                # Skip system messages
                if next_message['sender'] in ['Messages and calls are end-to-end encrypted', '']:
                    continue
                
                # Calculate time difference
                time_diff = next_message['timestamp'] - message['timestamp']
                
                # Skip if more than max response window
                if time_diff > timedelta(hours=self.max_response_window_hours):
                    break
                
                # Found a response
                response_found = True
                response_time_minutes = time_diff.total_seconds() / 60
                responder = next_message['sender']
                
                # Record this response pair
                response_pairs.append({
                    'original_sender': message['sender'],
                    'responder': responder,
                    'response_time_minutes': response_time_minutes,
                    'original_message': message['content'][:100],  # First 100 chars
                    'response_message': next_message['content'][:100],
                    'original_timestamp': message['timestamp'],
                    'response_timestamp': next_message['timestamp'],
                    'message_type': message['message_type']
                })
                
                # Initialize responder stats if not exists
                if responder not in responder_stats:
                    responder_stats[responder] = {
                        'total_responses': 0,
                        'response_times': [],
                        'responded_to_types': {},
                        'avg_response_time': 0
                    }
                
                # Update responder stats
                responder_stats[responder]['total_responses'] += 1
                responder_stats[responder]['response_times'].append(response_time_minutes)
                
                # Track response by message type
                message_type = message['message_type']
                if message_type not in responder_stats[responder]['responded_to_types']:
                    responder_stats[responder]['responded_to_types'][message_type] = {
                        'count': 0,
                        'times': []
                    }
                responder_stats[responder]['responded_to_types'][message_type]['count'] += 1
                responder_stats[responder]['responded_to_types'][message_type]['times'].append(response_time_minutes)
                
                break  # Found first response, stop looking
            
            # If no response found, mark as ignored
            if not response_found:
                ignored_messages.append({
                    'timestamp': message['timestamp'],
                    'sender': message['sender'],
                    'message': message['content'][:100],
                    'message_type': message['message_type'],
                    'ignored_duration_hours': (datetime.now() - message['timestamp']).total_seconds() / 3600
                })
        
        # Calculate average response times for each responder
        for responder in responder_stats:
            stats = responder_stats[responder]
            if stats['response_times']:
                stats['avg_response_time'] = np.mean(stats['response_times'])
                stats['median_response_time'] = np.median(stats['response_times'])
                stats['min_response_time'] = np.min(stats['response_times'])
                stats['max_response_time'] = np.max(stats['response_times'])
            else:
                stats['avg_response_time'] = 0
                stats['median_response_time'] = 0
                stats['min_response_time'] = 0
                stats['max_response_time'] = 0
        
        self.responder_analysis = {
            'responder_stats': responder_stats,
            'ignored_messages': ignored_messages,
            'response_pairs': response_pairs
        }
        
        return responder_stats, ignored_messages, response_pairs
    
    def generate_kpis(self) -> Dict:
        """Generate Key Performance Indicators from the responder analysis."""
        if not self.responder_analysis:
            self.analyze_responder_performance()
        
        responder_stats = self.responder_analysis['responder_stats']
        ignored_messages = self.responder_analysis['ignored_messages']
        
        total_responses = sum(stats['total_responses'] for stats in responder_stats.values())
        total_ignored = len(ignored_messages)
        total_conversations = total_responses + total_ignored
        
        if total_responses > 0:
            all_response_times = []
            for stats in responder_stats.values():
                all_response_times.extend(stats['response_times'])
            
            avg_response_time = np.mean(all_response_times)
            median_response_time = np.median(all_response_times)
            min_response_time = np.min(all_response_times)
            max_response_time = np.max(all_response_times)
        else:
            avg_response_time = median_response_time = min_response_time = max_response_time = 0
        
        response_rate = (total_responses / total_conversations * 100) if total_conversations > 0 else 0
        
        # Analyze by message type
        type_stats = {}
        for ignored_msg in ignored_messages:
            msg_type = ignored_msg['message_type']
            if msg_type not in type_stats:
                type_stats[msg_type] = {
                    'total_messages': 0,
                    'responded_messages': 0,
                    'ignored_messages': 0,
                    'response_times': []
                }
            type_stats[msg_type]['total_messages'] += 1
            type_stats[msg_type]['ignored_messages'] += 1
        
        # Add responded messages by type
        for responder_stats_data in responder_stats.values():
            for msg_type, type_data in responder_stats_data['responded_to_types'].items():
                if msg_type not in type_stats:
                    type_stats[msg_type] = {
                        'total_messages': 0,
                        'responded_messages': 0,
                        'ignored_messages': 0,
                        'response_times': []
                    }
                type_stats[msg_type]['total_messages'] += type_data['count']
                type_stats[msg_type]['responded_messages'] += type_data['count']
                type_stats[msg_type]['response_times'].extend(type_data['times'])
        
        # Calculate type-specific metrics
        for msg_type in type_stats:
            stats = type_stats[msg_type]
            if stats['response_times']:
                stats['avg_response_time'] = np.mean(stats['response_times'])
                stats['response_rate'] = stats['responded_messages'] / stats['total_messages'] * 100
            else:
                stats['avg_response_time'] = 0
                stats['response_rate'] = 0
        
        return {
            'total_conversations': total_conversations,
            'total_responses': total_responses,
            'total_ignored': total_ignored,
            'response_rate_percent': response_rate,
            'avg_response_time_minutes': avg_response_time,
            'median_response_time_minutes': median_response_time,
            'min_response_time_minutes': min_response_time,
            'max_response_time_minutes': max_response_time,
            'responder_statistics': responder_stats,
            'message_type_statistics': type_stats,
            'ignored_messages': ignored_messages,
            'analysis_period': {
                'start_date': min([msg['timestamp'] for msg in self.messages]) if self.messages else None,
                'end_date': max([msg['timestamp'] for msg in self.messages]) if self.messages else None,
                'total_messages': len(self.messages)
            }
        }
    
    def export_to_excel(self, output_file: str = 'nocdc_responder_analysis.xlsx'):
        """Export analysis results to Excel file."""
        if not self.responder_analysis:
            self.analyze_responder_performance()
        
        responder_stats = self.responder_analysis['responder_stats']
        ignored_messages = self.responder_analysis['ignored_messages']
        response_pairs = self.responder_analysis['response_pairs']
        kpis = self.generate_kpis()
        
        # Responder Performance DataFrame
        responder_df = pd.DataFrame([
            {
                'Responder': responder,
                'Total_Responses': stats['total_responses'],
                'Avg_Response_Time_Minutes': round(stats['avg_response_time'], 2),
                'Median_Response_Time_Minutes': round(stats['median_response_time'], 2),
                'Min_Response_Time_Minutes': round(stats['min_response_time'], 2),
                'Max_Response_Time_Minutes': round(stats['max_response_time'], 2)
            }
            for responder, stats in responder_stats.items()
        ])
        
        # Response Pairs DataFrame
        response_pairs_df = pd.DataFrame(response_pairs)
        
        # Ignored Messages DataFrame
        ignored_df = pd.DataFrame([
            {
                'Timestamp': msg['timestamp'],
                'Sender': msg['sender'],
                'Message': msg['message'],
                'Message_Type': msg['message_type'],
                'Ignored_Duration_Hours': round(msg['ignored_duration_hours'], 2)
            }
            for msg in ignored_messages
        ])
        
        # KPI Summary
        kpi_df = pd.DataFrame([
            {'Metric': 'Total Conversations', 'Value': kpis['total_conversations']},
            {'Metric': 'Total Responses', 'Value': kpis['total_responses']},
            {'Metric': 'Total Ignored', 'Value': kpis['total_ignored']},
            {'Metric': 'Response Rate (%)', 'Value': round(kpis['response_rate_percent'], 2)},
            {'Metric': 'Avg Response Time (min)', 'Value': round(kpis['avg_response_time_minutes'], 2)},
            {'Metric': 'Median Response Time (min)', 'Value': round(kpis['median_response_time_minutes'], 2)},
            {'Metric': 'Min Response Time (min)', 'Value': round(kpis['min_response_time_minutes'], 2)},
            {'Metric': 'Max Response Time (min)', 'Value': round(kpis['max_response_time_minutes'], 2)},
            {'Metric': 'Total Messages', 'Value': kpis['analysis_period']['total_messages']}
        ])
        
        # Message Type Performance
        type_df = pd.DataFrame([
            {
                'Message_Type': msg_type,
                'Total_Messages': stats['total_messages'],
                'Responded_Messages': stats['responded_messages'],
                'Ignored_Messages': stats['ignored_messages'],
                'Response_Rate_Percent': round(stats['response_rate'], 2),
                'Avg_Response_Time_Minutes': round(stats['avg_response_time'], 2)
            }
            for msg_type, stats in kpis['message_type_statistics'].items()
        ])
        
        # Response Time Distribution
        all_response_times = []
        for stats in responder_stats.values():
            all_response_times.extend(stats['response_times'])
        
        if all_response_times:
            # Create time ranges
            ranges = ['0-30 min', '30min-2h', '2-6 hours', '6-12 hours', '12-24 hours', '24+ hours']
            range_counts = [
                len([t for t in all_response_times if 0 <= t < 30]),
                len([t for t in all_response_times if 30 <= t < 120]),
                len([t for t in all_response_times if 120 <= t < 360]),
                len([t for t in all_response_times if 360 <= t < 720]),
                len([t for t in all_response_times if 720 <= t < 1440]),
                len([t for t in all_response_times if t >= 1440])
            ]
            
            timing_df = pd.DataFrame({
                'Response_Time_Range': ranges,
                'Count': range_counts
            })
        else:
            timing_df = pd.DataFrame({
                'Response_Time_Range': ['No responses found'],
                'Count': [0]
            })
        
        # All Messages
        all_messages_df = pd.DataFrame([
            {
                'Timestamp': msg['timestamp'],
                'Sender': msg['sender'],
                'Content': msg['content'],
                'Is_Conversation_Starter': msg['is_conversation_starter'],
                'Message_Type': msg['message_type'],
                'Message_Length': msg['message_length']
            }
            for msg in self.messages
        ])
        
        # Write to Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            responder_df.to_excel(writer, sheet_name='Responder Performance', index=False)
            response_pairs_df.to_excel(writer, sheet_name='Response Pairs', index=False)
            ignored_df.to_excel(writer, sheet_name='Ignored Messages', index=False)
            kpi_df.to_excel(writer, sheet_name='KPI Summary', index=False)
            type_df.to_excel(writer, sheet_name='Message Type Performance', index=False)
            timing_df.to_excel(writer, sheet_name='Timing Analysis', index=False)
            all_messages_df.to_excel(writer, sheet_name='All Messages', index=False)
        
        print(f"Analysis exported to {output_file}")
        return output_file

def main():
    """Main function to run the analysis."""
    chat_file = '/home/enki/whatsapp_data/NOCDCPlanning .txt'
    
    print("🔍 Starting RESPONDER Response Time Analysis...")
    print(f"📁 Analyzing file: {chat_file}")
    print("⚠️  Measuring how long each person takes to respond to others")
    
    # Initialize parser
    parser = ResponderAnalysisParser(chat_file)
    
    # Parse messages
    print("📝 Parsing messages...")
    messages = parser.parse_chat_file()
    print(f"✅ Parsed {len(messages)} messages")
    
    # Detect conversation threads
    print("🧵 Detecting conversation threads...")
    threads = parser.detect_conversation_threads()
    print(f"✅ Detected {len(threads)} conversation threads")
    
    # Analyze responder performance
    print("⏱️ Analyzing responder performance...")
    responder_stats, ignored_messages, response_pairs = parser.analyze_responder_performance()
    print(f"✅ Analyzed {len(responder_stats)} responders")
    print(f"⚠️  Found {len(ignored_messages)} ignored messages")
    print(f"📋 Found {len(response_pairs)} response pairs")
    
    # Generate KPIs
    print("📊 Generating KPIs...")
    kpis = parser.generate_kpis()
    
    # Print summary
    print("\n" + "="*70)
    print("📈 RESPONDER RESPONSE TIME ANALYSIS SUMMARY")
    print("="*70)
    print(f"Total Conversations: {kpis['total_conversations']}")
    print(f"Total Responses: {kpis['total_responses']}")
    print(f"Total Ignored: {kpis['total_ignored']}")
    print(f"Response Rate: {kpis['response_rate_percent']:.1f}%")
    print(f"Average Response Time: {kpis['avg_response_time_minutes']:.1f} minutes ({kpis['avg_response_time_minutes']/60:.1f} hours)")
    print(f"Median Response Time: {kpis['median_response_time_minutes']:.1f} minutes ({kpis['median_response_time_minutes']/60:.1f} hours)")
    print(f"Analysis Period: {kpis['analysis_period']['start_date']} to {kpis['analysis_period']['end_date']}")
    print(f"Total Messages: {kpis['analysis_period']['total_messages']}")
    
    print("\n👥 RESPONDER PERFORMANCE:")
    print("-" * 40)
    for responder, stats in kpis['responder_statistics'].items():
        print(f"{responder}:")
        print(f"  - Total Responses: {stats['total_responses']}")
        print(f"  - Avg Response Time: {stats['avg_response_time']:.1f} min ({stats['avg_response_time']/60:.1f} hours)")
        print(f"  - Median Response Time: {stats['median_response_time']:.1f} min")
    
    print("\n📋 MESSAGE TYPE PERFORMANCE:")
    print("-" * 40)
    for msg_type, stats in kpis['message_type_statistics'].items():
        print(f"{msg_type}:")
        print(f"  - Total Messages: {stats['total_messages']}")
        print(f"  - Response Rate: {stats['response_rate']:.1f}%")
        print(f"  - Ignored Messages: {stats['ignored_messages']}")
        print(f"  - Avg Response Time: {stats['avg_response_time']:.1f} min ({stats['avg_response_time']/60:.1f} hours)")
    
    if ignored_messages:
        print("\n⚠️  IGNORED MESSAGES (Top 5):")
        print("-" * 40)
        for i, msg in enumerate(ignored_messages[:5]):
            print(f"{i+1}. {msg['sender']}: {msg['message'][:50]}...")
            print(f"   Type: {msg['message_type']}, Ignored for: {msg['ignored_duration_hours']:.1f} hours")
    
    # Export to Excel
    print("\n💾 Exporting to Excel...")
    output_file = parser.export_to_excel()
    print(f"✅ Analysis exported to: {output_file}")
    
    return parser, kpis

if __name__ == "__main__":
    parser, kpis = main()
