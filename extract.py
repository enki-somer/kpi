import re
import pandas as pd
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

@dataclass
class Message:
    timestamp: datetime
    sender: str
    sender_type: str  # 'customer' or 'support'
    content: str
    message_type: str
    language: str
    has_ticket_id: bool
    ticket_ids: List[str]

@dataclass
class Issue:
    issue_id: str
    ticket_ids: List[str]
    reporter: str
    initial_message: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    messages: List[Message]
    first_response_time: Optional[timedelta]
    resolution_time: Optional[timedelta]
    total_responses: int
    category: str
    language: str
    support_participants: Set[str]

class AccurateWhatsAppAnalyzer:
    def __init__(self, members_file: str = 'members.json'):
        """Initialize with member configuration"""
        self.messages = []
        self.issues = []
        self.customers = set()
        self.support_staff = set()
        self.all_senders = set()
        
        # Load or create member configuration
        self.load_members_config(members_file)
        
        # Multilingual patterns based on actual chat
        self.patterns = self._init_patterns()
    
    def load_members_config(self, filepath: str):
        """Load member roles from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.customers = set(config.get('customers', []))
                self.support_staff = set(config.get('support_staff', []))
                print(f"Loaded config: {len(self.customers)} customers, {len(self.support_staff)} support staff")
        except FileNotFoundError:
            # Create template
            template = {
                "_instructions": "Define members by their exact names or phone numbers as they appear in the chat",
                "customers": [
                    "+964 783 443 6137",
                    "+964 790 277 3316",
                    "+964 781 203 9859",
                    "+964 771 167 8385"
                ],
                "support_staff": [
                    "Omar Noc",
                    "+964 770 693 8940",
                    "+964 782 128 1984",
                    "Ahmed Isam",
                    "علي It ايرثلنك",
                    "+964 770 495 3348",
                    "Ali Oudah Noc",
                    "حيدر حلاوة",
                    "+964 780 852 5298",
                    "Farouk",
                    "+964 780 255 8403"
                ]
            }
            with open('members_template.json', 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            print(f"Created template at 'members_template.json'. Please fill it and rename to '{filepath}'")
            self.customers = set(template['customers'])
            self.support_staff = set(template['support_staff'])
    
    def _init_patterns(self) -> dict:
        """Initialize multilingual patterns based on actual chat analysis"""
        return {
            'issue_keywords': {
                'arabic': [
                    'مشكلة', 'عطل', 'خطأ', 'طفت', 'طافي', 'طفه', 'منقطع',
                    'ماجابه', 'ماجابها', 'مجابه', 'مجابها', 'مو شغال', 'ما يشتغل',
                    'بوية', 'بويه', 'بوينت', 'بوينتات', 'بورت', 'بورتات',
                    'قطع', 'قطوعات', 'down', 'offline', 'لطش', 'معلق',
                    'طافيه', 'طافي', 'طفت', 'قطوعات', 'بورتات طفت', 'بورتات طافي',
                    'مجابه الزابكس', 'ماجابها الزابكس', 'ماجابه الزابكس',
                    'قطع ما بين', 'قطع مجايبه', 'قطوعات مجايبها'
                ],
                'english': [
                    'issue', 'problem', 'error', 'down', 'offline', 'not working',
                    'failed', 'fault', 'port down', 'ports down', 'link down',
                    'trigger', 'alarm', 'unknown status', 'ticket', 'ticketid'
                ]
            },
            'acknowledgment': {
                'arabic': [
                    'تمام', 'باشر', 'اوكي', 'حاضر', 'فهمت', 'وصل',
                    'هسه اجيك', 'هسه نجيك', 'شوفه', 'راح اشوف', 'دلل',
                    'هسه اشوفها', 'هسه اجيكه'
                ],
                'english': [
                    'ok', 'okay', 'got it', 'noted', 'checking', 'will check',
                    'looking into'
                ]
            },
            'resolution': {
                'arabic': [
                    'تم', 'انحل', 'اشتغل', 'شغال', 'done', 'solved', 'fixed',
                    'recheck', 'كملن', 'انتهى', 'خلاص', 'ضبط', 'تمام', 'ok',
                    'عاشت ايدك', 'وايدك', 'تدلل', 'ممنون', 'شكرا', 'thank you'
                ],
                'english': [
                    'done', 'fixed', 'solved', 'resolved', 'completed',
                    'recheck', 'working now', 'all good', 'ok', 'solved',
                    'thank you', 'thanks', 'welcome'
                ]
            },
            'request_action': {
                'arabic': [
                    'ممكن', 'بلازحمه', 'اذا ممكن', 'تقدر', 'لو سمحت',
                    'تجيك', 'تشوف', 'تعدل', 'تمسحها', 'تلغوها'
                ],
                'english': [
                    'can you', 'could you', 'please', 'would you', 'kindly'
                ]
            },
            'follow_up': {
                'arabic': [
                    'شلونك', 'وين وصل', 'شنو صار', 'كملن', 'لسا', 'بعد',
                    'شوفت', 'انت ذهب', 'هسه'
                ],
                'english': [
                    'any update', 'status', 'what about', 'still', 'yet'
                ]
            },
            'ticket_pattern': r'\b\d{7}\b',  # 7-digit ticket IDs like 9563926
            'greeting': {
                'arabic': ['سلام عليكم', 'صباح الخير', 'مساء الخير', 'هلو', 'مرحبا'],
                'english': ['hello', 'hi', 'good morning', 'good evening']
            }
        }
    
    def parse_whatsapp_file(self, filepath: str):
        """Parse WhatsApp chat export with robust handling"""
        print(f"\n{'='*60}")
        print(f"Parsing WhatsApp chat: {filepath}")
        print(f"{'='*60}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clean special Unicode characters that appear in WhatsApp exports
        content = re.sub(r'[\u202F\u00A0\u2068\u2069]', ' ', content)  # Various special spaces and marks
        
        # The exact pattern for your format: M/D/YY, H:MM AM/PM - Sender: Message
        # This pattern captures multi-line messages correctly
        pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2})\s*([AP]M)\s+-\s+([^:]+?):\s+((?:(?!\d{1,2}/\d{1,2}/\d{2,4},\s+\d{1,2}:\d{2}).)+)'
        
        patterns = [pattern]
        
        raw_messages = []
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            if matches:
                print(f"✓ Matched pattern {patterns.index(pattern) + 1}: {len(matches)} messages")
                
                for match in matches:
                    date_str, time_str, am_pm, sender, message = match
                    
                    # Skip system messages
                    if self._is_system_message(message):
                        continue
                    
                    # Parse timestamp
                    timestamp = self._parse_timestamp(date_str, time_str, am_pm)
                    if not timestamp:
                        continue
                    
                    sender = sender.strip()
                    message = message.strip()
                    
                    # Extract ticket IDs
                    ticket_ids = re.findall(self.patterns['ticket_pattern'], message)
                    
                    raw_messages.append({
                        'timestamp': timestamp,
                        'sender': sender,
                        'content': message,
                        'has_ticket_id': len(ticket_ids) > 0,
                        'ticket_ids': ticket_ids,
                        'language': self._detect_language(message)
                    })
                
                break  # Use first successful pattern
        
        # Sort by timestamp
        raw_messages.sort(key=lambda x: x['timestamp'])
        self.raw_messages = raw_messages
        
        # Collect all unique senders
        self.all_senders = set(msg['sender'] for msg in raw_messages)
        
        print(f"\n📊 Parsing Results:")
        print(f"   Total messages: {len(raw_messages)}")
        print(f"   Unique senders: {len(self.all_senders)}")
        print(f"   Date range: {raw_messages[0]['timestamp'].date()} to {raw_messages[-1]['timestamp'].date()}")
        
        # Show language distribution
        lang_dist = defaultdict(int)
        for msg in raw_messages:
            lang_dist[msg['language']] += 1
        print(f"   Language distribution: {dict(lang_dist)}")
        
        return len(raw_messages)
    
    def _is_system_message(self, content: str) -> bool:
        """Identify system messages to skip"""
        system_indicators = [
            'Messages and calls are end-to-end encrypted',
            'created group',
            'added you',
            '<Media omitted>',
            'This message was deleted',
            'You were added',
            'removed',
            'changed the group',
            'joined using',
            'left',
            'Learn more'
        ]
        return any(indicator in content for indicator in system_indicators)
    
    def _parse_timestamp(self, date_str: str, time_str: str, am_pm: str = None) -> Optional[datetime]:
        """Parse various timestamp formats"""
        # Remove special characters and extra spaces
        time_str = time_str.strip()
        date_str = date_str.strip()
        
        # If AM/PM is provided separately, combine it with time
        if am_pm:
            time_str = f"{time_str} {am_pm}"
        
        # Your format is: M/D/YY H:MM AM/PM
        formats = [
            "%m/%d/%y %I:%M %p",
            "%m/%d/%y %I:%M %PM",
            "%d/%m/%y %I:%M %p",
            "%m/%d/%Y %I:%M %p",
            "%d/%m/%Y %I:%M %p",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(f"{date_str} {time_str}", fmt)
            except:
                continue
        
        return None
    
    def _detect_language(self, text: str) -> str:
        """Detect if text is Arabic, English, or mixed"""
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if arabic_chars > english_chars * 2:
            return 'arabic'
        elif english_chars > arabic_chars * 2:
            return 'english'
        else:
            return 'mixed'
    
    def classify_members(self):
        """Classify members and handle unclassified"""
        print(f"\n{'='*60}")
        print("Member Classification")
        print(f"{'='*60}")
        
        unclassified = self.all_senders - self.customers - self.support_staff
        
        if unclassified:
            print(f"\n⚠️  Found {len(unclassified)} unclassified members:")
            for i, sender in enumerate(sorted(unclassified), 1):
                # Analyze message patterns
                sender_messages = [m for m in self.raw_messages if m['sender'] == sender]
                analysis = self._analyze_sender_behavior(sender_messages)
                
                print(f"\n{i}. {sender}")
                print(f"   Messages: {len(sender_messages)}")
                print(f"   Issue reports: {analysis['issue_count']}")
                print(f"   Responses: {analysis['response_count']}")
                print(f"   Suggestion: {'CUSTOMER' if analysis['likely_customer'] else 'SUPPORT'}")
                
                # Auto-classify based on behavior
                if analysis['likely_customer']:
                    self.customers.add(sender)
                else:
                    self.support_staff.add(sender)
        
        print(f"\n✓ Final Classification:")
        print(f"   Customers: {len(self.customers)}")
        print(f"   Support Staff: {len(self.support_staff)}")
        
        # Save updated classification
        self._save_classification()
    
    def _analyze_sender_behavior(self, messages: List[dict]) -> dict:
        """Analyze sender behavior to classify as customer or support"""
        issue_count = 0
        response_count = 0
        has_acknowledgments = 0
        has_resolutions = 0
        
        for msg in messages:
            content_lower = msg['content'].lower()
            
            # Check for issue reporting
            for keyword in self.patterns['issue_keywords']['arabic'] + self.patterns['issue_keywords']['english']:
                if keyword in content_lower:
                    issue_count += 1
                    break
            
            # Check for support responses
            for keyword in self.patterns['acknowledgment']['arabic'] + self.patterns['acknowledgment']['english']:
                if keyword in content_lower:
                    has_acknowledgments += 1
                    break
            
            for keyword in self.patterns['resolution']['arabic'] + self.patterns['resolution']['english']:
                if keyword in content_lower:
                    has_resolutions += 1
                    break
            
            # Check for "done", "recheck" pattern (typical support response)
            if re.search(r'\b(done|recheck|تمام حبيبي|هسه اجيك)\b', content_lower):
                response_count += 1
        
        # Decision logic
        likely_customer = (issue_count > response_count) and (has_resolutions < 3)
        
        return {
            'issue_count': issue_count,
            'response_count': response_count,
            'has_acknowledgments': has_acknowledgments,
            'has_resolutions': has_resolutions,
            'likely_customer': likely_customer
        }
    
    def _save_classification(self):
        """Save current classification"""
        config = {
            'customers': sorted(list(self.customers)),
            'support_staff': sorted(list(self.support_staff))
        }
        with open('members_classified.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved classification to 'members_classified.json'")
    
    def classify_messages(self):
        """Classify each message type"""
        print(f"\n{'='*60}")
        print("Classifying Messages")
        print(f"{'='*60}")
        
        for msg_data in self.raw_messages:
            sender = msg_data['sender']
            content = msg_data['content'].lower()
            
            # Determine sender type
            if sender in self.customers:
                sender_type = 'customer'
            elif sender in self.support_staff:
                sender_type = 'support'
            else:
                sender_type = 'unknown'
            
            # Classify message type
            message_type = self._classify_message_type(
                sender_type, content, msg_data['has_ticket_id']
            )
            
            message = Message(
                timestamp=msg_data['timestamp'],
                sender=sender,
                sender_type=sender_type,
                content=msg_data['content'],
                message_type=message_type,
                language=msg_data['language'],
                has_ticket_id=msg_data['has_ticket_id'],
                ticket_ids=msg_data['ticket_ids']
            )
            
            self.messages.append(message)
        
        # Show statistics
        type_counts = defaultdict(int)
        for msg in self.messages:
            type_counts[msg.message_type] += 1
        
        print(f"\n📊 Message Classification:")
        for msg_type, count in sorted(type_counts.items()):
            print(f"   {msg_type}: {count}")
    
    def _classify_message_type(self, sender_type: str, content: str, has_ticket: bool) -> str:
        """Classify individual message type with improved accuracy"""
        content_lower = content.lower()
        
        if sender_type == 'customer':
            # Check for issue report with more comprehensive patterns
            issue_indicators = [
                'طفت', 'طافي', 'قطع', 'مشكلة', 'بورت', 'down', 'error',
                'ماجابه', 'مجابه', 'ماجابها', 'مجابها', 'طافيه',
                'بورتات طفت', 'بورتات طافي', 'قطوعات', 'لطش'
            ]
            
            if any(indicator in content_lower for indicator in issue_indicators):
                return 'issue_report'
            elif has_ticket:
                return 'issue_report'  # Ticket mention usually indicates new issue
            elif self._contains_keywords(content, self.patterns['follow_up']):
                return 'follow_up'
            else:
                return 'general'
        
        elif sender_type == 'support':
            # Check for resolution with more comprehensive patterns
            resolution_indicators = [
                'تمام', 'done', 'recheck', 'ok', 'solved', 'fixed',
                'عاشت ايدك', 'وايدك', 'تدلل', 'ممنون', 'شكرا',
                'thank you', 'welcome', 'كملن', 'انتهى'
            ]
            
            if any(indicator in content_lower for indicator in resolution_indicators):
                return 'resolution'
            elif self._contains_keywords(content, self.patterns['acknowledgment']):
                return 'acknowledgment'
            elif self._contains_keywords(content, self.patterns['request_action']):
                return 'request_info'
            else:
                return 'response'
        
        return 'other'
    
    def _contains_keywords(self, content: str, keyword_dict: dict) -> bool:
        """Check if content contains any keywords from both languages"""
        for lang in ['arabic', 'english']:
            if lang in keyword_dict:
                for keyword in keyword_dict[lang]:
                    if keyword in content:
                        return True
        return False
    
    def group_into_issues(self):
        """Group messages into distinct issues with improved accuracy"""
        print(f"\n{'='*60}")
        print("Grouping Messages into Issues")
        print(f"{'='*60}")
        
        current_issue = None
        issue_counter = 1
        max_gap = timedelta(hours=2)  # Reduced gap for better accuracy
        
        for i, msg in enumerate(self.messages):
            
            # Start new issue on issue_report from customer
            if msg.message_type == 'issue_report' and msg.sender_type == 'customer':
                
                # Close previous issue if exists
                if current_issue and current_issue.status == 'open':
                    current_issue.status = 'pending'
                    current_issue.end_time = current_issue.messages[-1].timestamp
                
                # Create new issue with precise start timestamp
                issue_id = f"ISSUE_{issue_counter:04d}"
                current_issue = Issue(
                    issue_id=issue_id,
                    ticket_ids=msg.ticket_ids.copy(),
                    reporter=msg.sender,
                    initial_message=msg.content,
                    start_time=msg.timestamp,
                    end_time=None,
                    status='open',
                    messages=[msg],
                    first_response_time=None,
                    resolution_time=None,
                    total_responses=0,
                    category=self._categorize_issue(msg.content),
                    language=msg.language,
                    support_participants=set()
                )
                self.issues.append(current_issue)
                issue_counter += 1
                continue
            
            # Add message to current issue if exists
            if current_issue:
                time_gap = msg.timestamp - current_issue.messages[-1].timestamp
                
                # Check if message belongs to current issue
                belongs_to_issue = (
                    time_gap <= max_gap or 
                    any(tid in msg.ticket_ids for tid in current_issue.ticket_ids) or
                    (msg.sender_type == 'customer' and msg.message_type in ['follow_up', 'general'])
                )
                
                if belongs_to_issue:
                    current_issue.messages.append(msg)
                    
                    # Track support responses with precise timing
                    if msg.sender_type == 'support':
                        current_issue.support_participants.add(msg.sender)
                        
                        # Calculate first response time precisely
                        if current_issue.first_response_time is None:
                            if msg.message_type in ['acknowledgment', 'response', 'request_info']:
                                current_issue.first_response_time = msg.timestamp - current_issue.start_time
                                print(f"  📝 First response for {current_issue.issue_id}: {current_issue.first_response_time}")
                        
                        # Count responses
                        if msg.message_type in ['response', 'acknowledgment', 'request_info']:
                            current_issue.total_responses += 1
                        
                        # Check for resolution with precise timing
                        if msg.message_type == 'resolution':
                            current_issue.status = 'resolved'
                            current_issue.end_time = msg.timestamp
                            current_issue.resolution_time = msg.timestamp - current_issue.start_time
                            print(f"  ✅ Resolution for {current_issue.issue_id}: {current_issue.resolution_time}")
                    
                    # Add ticket IDs mentioned in conversation
                    for tid in msg.ticket_ids:
                        if tid not in current_issue.ticket_ids:
                            current_issue.ticket_ids.append(tid)
                else:
                    # Start new issue if gap is too large or different context
                    if msg.sender_type == 'customer' and msg.message_type in ['issue_report', 'general']:
                        # Close current issue
                        if current_issue.status == 'open':
                            current_issue.status = 'pending'
                            current_issue.end_time = current_issue.messages[-1].timestamp
                        
                        # Start new issue
                        issue_id = f"ISSUE_{issue_counter:04d}"
                        current_issue = Issue(
                            issue_id=issue_id,
                            ticket_ids=msg.ticket_ids.copy(),
                            reporter=msg.sender,
                            initial_message=msg.content,
                            start_time=msg.timestamp,
                            end_time=None,
                            status='open',
                            messages=[msg],
                            first_response_time=None,
                            resolution_time=None,
                            total_responses=0,
                            category=self._categorize_issue(msg.content),
                            language=msg.language,
                            support_participants=set()
                        )
                        self.issues.append(current_issue)
                        issue_counter += 1
        
        # Close remaining open issues with precise end times
        for issue in self.issues:
            if issue.status == 'open':
                issue.end_time = issue.messages[-1].timestamp
                if issue.first_response_time:
                    issue.status = 'pending'
                else:
                    issue.status = 'no_response'
        
        print(f"\n✓ Created {len(self.issues)} issues")
        
        # Show status distribution
        status_counts = defaultdict(int)
        for issue in self.issues:
            status_counts[issue.status] += 1
        
        print(f"\n📊 Issue Status Distribution:")
        for status, count in sorted(status_counts.items()):
            print(f"   {status}: {count}")
        
        # Show timing statistics
        response_times = [i.first_response_time for i in self.issues if i.first_response_time]
        resolution_times = [i.resolution_time for i in self.issues if i.resolution_time]
        
        if response_times:
            avg_response = sum(response_times, timedelta()) / len(response_times)
            print(f"\n⏱️  Timing Statistics:")
            print(f"   Average Response Time: {avg_response}")
            print(f"   Issues with Response: {len(response_times)}/{len(self.issues)}")
        
        if resolution_times:
            avg_resolution = sum(resolution_times, timedelta()) / len(resolution_times)
            print(f"   Average Resolution Time: {avg_resolution}")
            print(f"   Issues Resolved: {len(resolution_times)}/{len(self.issues)}")
    
    def _categorize_issue(self, content: str) -> str:
        """Categorize issue based on content"""
        content_lower = content.lower()
        
        categories = {
            'zabbix_monitoring': ['zabbix', 'زابكس', 'ماجابه الزابكس', 'مجابها الزابكس'],
            'port_down': ['port', 'بورت', 'بورتات', 'ports down', 'link down'],
            'temperature': ['temperature', 'حرارة', 'تمبرجر', 'trigger'],
            'outage': ['قطع', 'قطوعات', 'down', 'offline', 'طفت', 'منقطع'],
            'configuration': ['edit', 'change', 'تعديل', 'عدل', 'oid', 'class'],
            'alarm': ['alarm', 'الرم', 'مشكلة', 'error']
        }
        
        for category, keywords in categories.items():
            if any(kw in content_lower for kw in keywords):
                return category
        
        return 'other'
    
    def calculate_kpis(self) -> dict:
        """Calculate comprehensive KPIs with precise timing"""
        print(f"\n{'='*60}")
        print("Calculating KPIs")
        print(f"{'='*60}")
        
        if not self.issues:
            return {"error": "No issues found"}
        
        total_issues = len(self.issues)
        resolved = len([i for i in self.issues if i.status == 'resolved'])
        pending = len([i for i in self.issues if i.status == 'pending'])
        no_response = len([i for i in self.issues if i.status == 'no_response'])
        
        # Precise response times calculation
        response_times = [i.first_response_time for i in self.issues if i.first_response_time]
        if response_times:
            avg_response_time = sum(response_times, timedelta()) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = timedelta()
            min_response_time = None
            max_response_time = None
        
        # Precise resolution times calculation
        resolution_times = [i.resolution_time for i in self.issues if i.resolution_time]
        if resolution_times:
            avg_resolution_time = sum(resolution_times, timedelta()) / len(resolution_times)
            min_resolution_time = min(resolution_times)
            max_resolution_time = max(resolution_times)
        else:
            avg_resolution_time = timedelta()
            min_resolution_time = None
            max_resolution_time = None
        
        # Category distribution
        category_counts = defaultdict(int)
        for issue in self.issues:
            category_counts[issue.category] += 1
        
        # Reporter statistics
        reporter_counts = defaultdict(int)
        for issue in self.issues:
            reporter_counts[issue.reporter] += 1
        
        # Support staff performance with precise metrics
        support_performance = defaultdict(lambda: {
            'issues_handled': 0, 
            'responses': 0, 
            'avg_response_time': timedelta(),
            'resolutions': 0
        })
        
        for issue in self.issues:
            for support in issue.support_participants:
                support_performance[support]['issues_handled'] += 1
                
                # Count responses from this support member
                support_responses = sum(
                    1 for m in issue.messages 
                    if m.sender == support and m.sender_type == 'support'
                )
                support_performance[support]['responses'] += support_responses
                
                # Count resolutions by this support member
                support_resolutions = sum(
                    1 for m in issue.messages 
                    if m.sender == support and m.message_type == 'resolution'
                )
                support_performance[support]['resolutions'] += support_resolutions
        
        # Calculate average response times per support member
        for support, perf in support_performance.items():
            if perf['responses'] > 0:
                # This is a simplified calculation - in practice you'd track individual response times
                perf['avg_response_time'] = avg_response_time
        
        # Time-based analysis
        time_analysis = self._analyze_timing_patterns()
        
        kpis = {
            'total_issues': total_issues,
            'resolved_issues': resolved,
            'pending_issues': pending,
            'no_response_issues': no_response,
            'resolution_rate': (resolved / total_issues * 100) if total_issues > 0 else 0,
            'response_rate': (len(response_times) / total_issues * 100) if total_issues > 0 else 0,
            'avg_response_time_minutes': avg_response_time.total_seconds() / 60,
            'avg_resolution_time_hours': avg_resolution_time.total_seconds() / 3600,
            'min_response_time_minutes': min_response_time.total_seconds() / 60 if min_response_time else None,
            'max_response_time_minutes': max_response_time.total_seconds() / 60 if max_response_time else None,
            'min_resolution_time_hours': min_resolution_time.total_seconds() / 3600 if min_resolution_time else None,
            'max_resolution_time_hours': max_resolution_time.total_seconds() / 3600 if max_resolution_time else None,
            'category_distribution': dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True)),
            'top_reporters': dict(sorted(reporter_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'support_performance': dict(support_performance),
            'total_customers': len(self.customers),
            'total_support_staff': len(self.support_staff),
            'total_messages': len(self.messages),
            'timing_analysis': time_analysis
        }
        
        return kpis
    
    def _analyze_timing_patterns(self) -> dict:
        """Analyze timing patterns for better insights"""
        if not self.issues:
            return {}
        
        # Analyze by hour of day
        hour_distribution = defaultdict(int)
        for issue in self.issues:
            hour_distribution[issue.start_time.hour] += 1
        
        # Analyze by day of week
        weekday_distribution = defaultdict(int)
        for issue in self.issues:
            weekday_distribution[issue.start_time.strftime('%A')] += 1
        
        # Analyze response time distribution
        response_times = [i.first_response_time for i in self.issues if i.first_response_time]
        response_time_ranges = {
            'under_5_min': len([rt for rt in response_times if rt.total_seconds() < 300]),
            '5_to_15_min': len([rt for rt in response_times if 300 <= rt.total_seconds() < 900]),
            '15_to_30_min': len([rt for rt in response_times if 900 <= rt.total_seconds() < 1800]),
            '30_to_60_min': len([rt for rt in response_times if 1800 <= rt.total_seconds() < 3600]),
            'over_1_hour': len([rt for rt in response_times if rt.total_seconds() >= 3600])
        }
        
        return {
            'hour_distribution': dict(hour_distribution),
            'weekday_distribution': dict(weekday_distribution),
            'response_time_ranges': response_time_ranges
        }
    
    def generate_report(self) -> str:
        """Generate comprehensive report"""
        kpis = self.calculate_kpis()
        
        if 'error' in kpis:
            return f"Error: {kpis['error']}"
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║         WHATSAPP SUPPORT CHAT ANALYSIS REPORT                ║
╚══════════════════════════════════════════════════════════════╝

📊 OVERVIEW
{'─'*60}
Total Issues Identified      : {kpis['total_issues']}
Total Messages Analyzed      : {kpis['total_messages']}
Active Customers            : {kpis['total_customers']}
Support Staff Members       : {kpis['total_support_staff']}

🎯 KEY PERFORMANCE INDICATORS
{'─'*60}
Resolution Rate             : {kpis['resolution_rate']:.1f}%
Response Rate              : {kpis['response_rate']:.1f}%
Avg First Response Time    : {kpis['avg_response_time_minutes']:.1f} minutes
Avg Resolution Time        : {kpis['avg_resolution_time_hours']:.1f} hours
Min Response Time          : {kpis['min_response_time_minutes']:.1f} minutes
Max Response Time          : {kpis['max_response_time_minutes']:.1f} minutes
Min Resolution Time        : {kpis['min_resolution_time_hours']:.1f} hours
Max Resolution Time        : {kpis['max_resolution_time_hours']:.1f} hours

📈 ISSUE STATUS BREAKDOWN
{'─'*60}
✅ Resolved                 : {kpis['resolved_issues']} ({kpis['resolved_issues']/kpis['total_issues']*100:.1f}%)
⏳ Pending                  : {kpis['pending_issues']} ({kpis['pending_issues']/kpis['total_issues']*100:.1f}%)
❌ No Response              : {kpis['no_response_issues']} ({kpis['no_response_issues']/kpis['total_issues']*100:.1f}%)

🏷️  TOP ISSUE CATEGORIES
{'─'*60}"""
        
        for i, (category, count) in enumerate(list(kpis['category_distribution'].items())[:5], 1):
            pct = count / kpis['total_issues'] * 100
            report += f"\n{i}. {category.replace('_', ' ').title():25s} : {count:3d} ({pct:5.1f}%)"
        
        report += f"""

👥 TOP ISSUE REPORTERS
{'─'*60}"""
        
        for i, (reporter, count) in enumerate(list(kpis['top_reporters'].items())[:5], 1):
            report += f"\n{i}. {reporter:35s} : {count:3d} issues"
        
        report += f"""

👨‍💼 SUPPORT STAFF PERFORMANCE
{'─'*60}"""
        
        for staff, perf in sorted(kpis['support_performance'].items(), 
                                 key=lambda x: x[1]['issues_handled'], reverse=True)[:10]:
            report += f"\n• {staff:35s}"
            report += f"\n  └─ Issues Handled: {perf['issues_handled']:3d}  |  Total Responses: {perf['responses']:3d}  |  Resolutions: {perf['resolutions']:3d}"
        
        # Add timing analysis
        if 'timing_analysis' in kpis and kpis['timing_analysis']:
            timing = kpis['timing_analysis']
            
            report += f"""

⏰ TIMING ANALYSIS
{'─'*60}"""
            
            # Response time distribution
            if 'response_time_ranges' in timing:
                ranges = timing['response_time_ranges']
                report += f"\nResponse Time Distribution:"
                report += f"\n  Under 5 minutes    : {ranges['under_5_min']:3d} issues"
                report += f"\n  5-15 minutes       : {ranges['5_to_15_min']:3d} issues"
                report += f"\n  15-30 minutes      : {ranges['15_to_30_min']:3d} issues"
                report += f"\n  30-60 minutes      : {ranges['30_to_60_min']:3d} issues"
                report += f"\n  Over 1 hour        : {ranges['over_1_hour']:3d} issues"
            
            # Peak hours
            if 'hour_distribution' in timing and timing['hour_distribution']:
                peak_hours = sorted(timing['hour_distribution'].items(), key=lambda x: x[1], reverse=True)[:3]
                report += f"\n\nPeak Issue Hours:"
                for hour, count in peak_hours:
                    report += f"\n  {hour:02d}:00 - {hour+1:02d}:00 : {count:3d} issues"
        
        report += f"\n\n{'═'*60}\n"
        
        return report
    
    def export_to_excel(self, filename: str = 'support_analysis.xlsx'):
        """Export detailed analysis to Excel with proper datetime formatting"""
        print(f"\n{'='*60}")
        print(f"Exporting to Excel: {filename}")
        print(f"{'='*60}")
        
        # Prepare issues data with precise timestamps
        issues_data = []
        for issue in self.issues:
            # Calculate precise response and resolution times
            first_response_minutes = None
            resolution_hours = None
            
            if issue.first_response_time:
                first_response_minutes = round(issue.first_response_time.total_seconds() / 60, 2)
            
            if issue.resolution_time:
                resolution_hours = round(issue.resolution_time.total_seconds() / 3600, 2)
            
            issues_data.append({
                'Issue ID': issue.issue_id,
                'Ticket IDs': ', '.join(issue.ticket_ids) if issue.ticket_ids else 'N/A',
                'Reporter': issue.reporter,
                'Category': issue.category,
                'Language': issue.language,
                'Status': issue.status,
                'Start Time': issue.start_time,
                'End Time': issue.end_time,
                'First Response Time (minutes)': first_response_minutes,
                'Resolution Time (hours)': resolution_hours,
                'Total Responses': issue.total_responses,
                'Support Staff Involved': ', '.join(issue.support_participants),
                'Initial Message': issue.initial_message[:200],
                'Final Message': issue.messages[-1].content[:200] if issue.messages else '',
                'Message Count': len(issue.messages)
            })
        
        # Prepare message log with precise timestamps
        messages_data = []
        for msg in self.messages:
            messages_data.append({
                'Timestamp': msg.timestamp,
                'Sender': msg.sender,
                'Sender Type': msg.sender_type,
                'Message Type': msg.message_type,
                'Language': msg.language,
                'Has Ticket': msg.has_ticket_id,
                'Ticket IDs': ', '.join(msg.ticket_ids) if msg.ticket_ids else '',
                'Content': msg.content[:300]
            })
        
        # Create Excel file with proper formatting
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Issues sheet
            df_issues = pd.DataFrame(issues_data)
            df_issues.to_excel(writer, sheet_name='Issues', index=False)
            
            # Messages sheet
            df_messages = pd.DataFrame(messages_data)
            df_messages.to_excel(writer, sheet_name='Messages', index=False)
            
            # KPI Summary sheet
            kpis = self.calculate_kpis()
            kpi_data = [
                ['Metric', 'Value'],
                ['Total Issues', kpis['total_issues']],
                ['Resolved Issues', kpis['resolved_issues']],
                ['Pending Issues', kpis['pending_issues']],
                ['No Response', kpis['no_response_issues']],
                ['Resolution Rate (%)', f"{kpis['resolution_rate']:.1f}"],
                ['Response Rate (%)', f"{kpis['response_rate']:.1f}"],
                ['Avg Response Time (min)', f"{kpis['avg_response_time_minutes']:.1f}"],
                ['Avg Resolution Time (hrs)', f"{kpis['avg_resolution_time_hours']:.1f}"],
                ['Total Messages', kpis['total_messages']],
                ['Total Customers', kpis['total_customers']],
                ['Total Support Staff', kpis['total_support_staff']]
            ]
            df_kpi = pd.DataFrame(kpi_data[1:], columns=kpi_data[0])
            df_kpi.to_excel(writer, sheet_name='KPI Summary', index=False)
            
            # Category distribution
            cat_data = [[cat, count] for cat, count in kpis['category_distribution'].items()]
            df_cat = pd.DataFrame(cat_data, columns=['Category', 'Count'])
            df_cat.to_excel(writer, sheet_name='Categories', index=False)
            
            # Support performance
            perf_data = []
            for staff, perf in kpis['support_performance'].items():
                perf_data.append([
                    staff,
                    perf['issues_handled'],
                    perf['responses']
                ])
            df_perf = pd.DataFrame(perf_data, columns=['Support Staff', 'Issues Handled', 'Total Responses'])
            df_perf = df_perf.sort_values('Issues Handled', ascending=False)
            df_perf.to_excel(writer, sheet_name='Support Performance', index=False)
            
            # Timing Analysis sheet
            timing_data = []
            if 'timing_analysis' in kpis and kpis['timing_analysis']:
                timing = kpis['timing_analysis']
                
                # Response time ranges
                if 'response_time_ranges' in timing:
                    ranges = timing['response_time_ranges']
                    timing_data.extend([
                        ['Response Time Range', 'Count'],
                        ['Under 5 minutes', ranges['under_5_min']],
                        ['5-15 minutes', ranges['5_to_15_min']],
                        ['15-30 minutes', ranges['15_to_30_min']],
                        ['30-60 minutes', ranges['30_to_60_min']],
                        ['Over 1 hour', ranges['over_1_hour']],
                        ['', ''],
                        ['Hour of Day', 'Issue Count']
                    ])
                
                # Hour distribution
                if 'hour_distribution' in timing:
                    for hour, count in sorted(timing['hour_distribution'].items()):
                        timing_data.append([f"{hour:02d}:00", count])
            
            if timing_data:
                df_timing = pd.DataFrame(timing_data[1:], columns=timing_data[0])
                df_timing.to_excel(writer, sheet_name='Timing Analysis', index=False)
            
            # Apply datetime formatting to Excel sheets
            workbook = writer.book
            
            # Format Issues sheet datetime columns
            issues_sheet = writer.sheets['Issues']
            for col_num, col_name in enumerate(df_issues.columns, 1):
                if 'Time' in col_name and col_name not in ['First Response Time (minutes)', 'Resolution Time (hours)']:
                    # Format datetime columns
                    for row_num in range(2, len(df_issues) + 2):  # Skip header
                        cell = issues_sheet.cell(row=row_num, column=col_num)
                        if cell.value and isinstance(cell.value, datetime):
                            cell.number_format = 'MM/DD/YYYY HH:MM AM/PM'
            
            # Format Messages sheet datetime column
            messages_sheet = writer.sheets['Messages']
            timestamp_col = df_messages.columns.get_loc('Timestamp') + 1
            for row_num in range(2, len(df_messages) + 2):  # Skip header
                cell = messages_sheet.cell(row=row_num, column=timestamp_col)
                if cell.value and isinstance(cell.value, datetime):
                    cell.number_format = 'MM/DD/YYYY HH:MM AM/PM'
            
            # Auto-adjust column widths
            for sheet_name in writer.sheets:
                sheet = writer.sheets[sheet_name]
                for column in sheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                    sheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✓ Exported to {filename}")
        print(f"  Sheets: Issues, Messages, KPI Summary, Categories, Support Performance, Timing Analysis")
        print(f"  ✓ Applied proper datetime formatting")
        print(f"  ✓ Auto-adjusted column widths")


def main():
    """Main execution function"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     WhatsApp Support Chat Analyzer                          ║
║     Advanced Issue Tracking & KPI Analysis                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Initialize analyzer
    analyzer = AccurateWhatsAppAnalyzer('members.json')
    
    # Parse chat file
    chat_file = 'zabbix_chat.txt'
    
    try:
        msg_count = analyzer.parse_whatsapp_file(chat_file)
        if msg_count == 0:
            print("\n❌ No messages parsed! Check the file format.")
            print("💡 Try running the format detector to diagnose the issue.")
            return
    except FileNotFoundError:
        print(f"\n❌ Error: Chat file '{chat_file}' not found!")
        print("\nPlease ensure your WhatsApp chat export file is in the same directory.")
        return
    
    # Classify members
    analyzer.classify_members()
    
    # Classify messages
    analyzer.classify_messages()
    
    # Group into issues
    analyzer.group_into_issues()
    
    # Generate report
    report = analyzer.generate_report()
    print(report)
    
    # Save report to file
    with open('analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print("✓ Report saved to 'analysis_report.txt'")
    
    # Export to Excel
    analyzer.export_to_excel('support_analysis.xlsx')
    
    print(f"\n{'='*60}")
    print("Analysis Complete!")
    print(f"{'='*60}")
    print("\nGenerated Files:")
    print("  1. analysis_report.txt       - Detailed text report")
    print("  2. support_analysis.xlsx     - Excel workbook with all data")
    print("  3. members_classified.json   - Updated member classification")
    print("\n")


if __name__ == "__main__":
    main()


# ==============================================================================
# USAGE INSTRUCTIONS
# ==============================================================================
"""
SETUP:
------
1. Install required packages:
   pip install pandas openpyxl

2. Create members.json file with your team structure:
   {
       "customers": [
           "+964 783 443 6137",
           "+964 790 277 3316",
           "Field Agent Name"
       ],
       "support_staff": [
           "Omar Noc",
           "+964 770 693 8940",
           "+964 782 128 1984"
       ]
   }

3. Place your WhatsApp chat export file in the same directory
   (Default name: "WhatsApp Chat with Zabbix NOC+IT.txt")

RUNNING:
--------
python whatsapp_analyzer.py

CUSTOMIZATION:
--------------
To adjust for your specific chat patterns, modify:

1. Time gap for issue grouping (line ~485):
   max_gap = timedelta(hours=4)  # Increase if issues span longer

2. Keyword patterns (line ~121-157):
   Add your specific keywords for issue detection

3. Categories (line ~573):
   Add your specific issue categories

UNDERSTANDING OUTPUT:
--------------------
The script generates:

1. analysis_report.txt
   - Human-readable summary
   - Key metrics and statistics
   - Top reporters and categories

2. support_analysis.xlsx
   - Sheet 1 (Issues): All identified issues with details
   - Sheet 2 (Messages): Complete message log
   - Sheet 3 (KPI Summary): Key performance indicators
   - Sheet 4 (Categories): Issue category breakdown
   - Sheet 5 (Support Performance): Staff performance metrics

3. members_classified.json
   - Updated member classification
   - Includes auto-detected members
   - Use this for future runs

KEY METRICS EXPLAINED:
---------------------
- Resolution Rate: % of issues marked as resolved
- Response Rate: % of issues that received a response
- First Response Time: Time from issue report to first support response
- Resolution Time: Time from issue report to resolution

TIPS FOR ACCURACY:
-----------------
1. Ensure members.json is accurate for best results
2. Review auto-classified members in the output
3. Adjust keyword patterns for your terminology
4. Set appropriate time gaps for issue grouping
5. Check ticket ID pattern matches your system (currently 7 digits)
"""