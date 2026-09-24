"""
domestic-drama: Domestic Short Drama Engine for Douyin/Kuaishou
"""
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

class DramaPlatform(Enum):
    DOUYIN = 'douyin'
    KUAISHOU = 'kuaishou'

class DramaGenre(Enum):
    ROMANCE = 'romance'
    REVENGE = 'revenge'
    FAMILY = 'family'
    WORKPLACE = 'workplace'
    FANTASY = 'fantasy'
    CRIME = 'crime'

class EpisodeStatus(Enum):
    DRAFT = 'draft'
    PRODUCING = 'producing'
    REVIEW = 'review'
    PUBLISHED = 'published'
    REMOVED = 'removed'

@dataclass
class Character:
    """Character in a drama."""
    name: str
    role: str  # 'protagonist', 'antagonist', 'supporting'
    description: str
    age: int = 0
    
    def to_dict(self):
        return self.__dict__

@dataclass
class Episode:
    """Single episode."""
    episode_number: int
    title: str
    script: str
    duration_sec: int  # 60-300 sec typical
    status: EpisodeStatus = EpisodeStatus.DRAFT
    published_at: Optional[float] = None
    platform: Optional[DramaPlatform] = None
    
    def to_dict(self):
        return {
            'episode_number': self.episode_number,
            'title': self.title,
            'script': self.script,
            'duration_sec': self.duration_sec,
            'status': self.status.value,
            'published_at': self.published_at,
            'platform': self.platform.value if self.platform else None
        }

@dataclass
class DramaProject:
    """Complete drama project."""
    title: str
    genre: DramaGenre
    platform: DramaPlatform
    total_episodes: int
    description: str
    characters: List[Character] = field(default_factory=list)
    episodes: List[Episode] = field(default_factory=list)
    status: str = 'draft'
    target_audience: str = '18-35'
    
    def add_character(self, name: str, role: str, description: str, age: int = 0):
        self.characters.append(Character(name, role, description, age))
    
    def add_episode(self, ep_num: int, title: str, script: str, duration: int = 90):
        ep = Episode(ep_num, title, script, duration)
        self.episodes.append(ep)
        return ep
    
    def to_dict(self):
        return {
            'title': self.title,
            'genre': self.genre.value,
            'platform': self.platform.value,
            'total_episodes': self.total_episodes,
            'description': self.description,
            'characters': [c.to_dict() for c in self.characters],
            'episodes': [e.to_dict() for e in self.episodes],
            'status': self.status,
            'target_audience': self.target_audience
        }

class DramaEngine:
    """
    Short drama engine optimized for Chinese platforms.
    Handles vertical format, platform-specific rules, content review.
    """
    
    # Platform-specific constraints
    PLATFORM_RULES = {
        DramaPlatform.DOUYIN: {
            'max_duration': 300,  # 5 min max
            'min_duration': 15,    # 15 sec min
            'aspect_ratio': '9:16',
            'content_categories': ['romance', 'comedy', 'family', 'workplace'],
            'sensitive_words': ['gambling', 'illegal'],
            'max_episodes': 100,
        },
        DramaPlatform.KUAISHOU: {
            'max_duration': 180,
            'min_duration': 15,
            'aspect_ratio': '9:16',
            'content_categories': ['romance', 'comedy', 'family', 'revenge'],
            'sensitive_words': ['gambling', 'illegal'],
            'max_episodes': 50,
        }
    }
    
    def __init__(self, platform: DramaPlatform = DramaPlatform.DOUYIN):
        self.platform = platform
        self.rules = self.PLATFORM_RULES[platform]
        self.projects: Dict[str, DramaProject] = {}
        self.review_queue: List[str] = []
    
    def create_project(self, title: str, genre: DramaGenre, 
                      total_episodes: int, description: str = '') -> DramaProject:
        """Create a new drama project."""
        if genre not in [DramaGenre(g) for g in self.rules['content_categories']]:
            raise ValueError(f"Genre {genre} not supported on {self.platform}")
        
        project_id = str(uuid.uuid4())[:8]
        project = DramaProject(
            title=title,
            genre=genre,
            platform=self.platform,
            total_episodes=total_episodes,
            description=description
        )
        self.projects[project_id] = project
        return project
    
    def create_episode(self, project_id: str, ep_num: int, 
                      title: str, script: str, duration: int = 90) -> Episode:
        """Create an episode for a project."""
        project = self.projects.get(project_id)
        if not project:
            raise KeyError(f"Project {project_id} not found")
        
        # Validate duration
        if duration < self.rules['min_duration']:
            duration = self.rules['min_duration']
        if duration > self.rules['max_duration']:
            duration = self.rules['max_duration']
        
        ep = project.add_episode(ep_num, title, script, duration)
        return ep
    
    def check_content(self, text: str) -> Dict:
        """
        Check content against platform rules.
        Returns review result.
        """
        issues = []
        text_lower = text.lower()
        
        for word in self.rules['sensitive_words']:
            if word in text_lower:
                issues.append(f"Sensitive word detected: {word}")
        
        # Check duration
        if len(text) > 5000:
            issues.append("Script too long for platform limits")
        
        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'platform': self.platform.value
        }
    
    def submit_for_review(self, project_id: str, episode_number: int = None):
        """Submit project or episode for content review."""
        project = self.projects.get(project_id)
        if not project:
            return False
        
        if episode_number is None:
            # Submit entire project
            all_passed = True
            for ep in project.episodes:
                result = self.check_content(ep.script)
                if not result['passed']:
                    all_passed = False
                    self.review_queue.append(f"{project_id}-ep{ep.episode_number}")
            if all_passed:
                project.status = 'review'
            return all_passed
        else:
            # Submit single episode
            for ep in project.episodes:
                if ep.episode_number == episode_number:
                    result = self.check_content(ep.script)
                    if result['passed']:
                        ep.status = EpisodeStatus.REVIEW
                    else:
                        self.review_queue.append(f"{project_id}-ep{ep.episode_number}")
                    return result['passed']
        return False
    
    def publish(self, project_id: str, platform: Optional[DramaPlatform] = None) -> bool:
        """Publish all reviewed episodes."""
        project = self.projects.get(project_id)
        if not project:
            return False
        
        target = platform or project.platform
        published = 0
        for ep in project.episodes:
            if ep.status == EpisodeStatus.REVIEW:
                ep.status = EpisodeStatus.PUBLISHED
                ep.published_at = time.time()
                ep.platform = target
                published += 1
        
        if published == len(project.episodes) and project.episodes:
            project.status = 'published'
        return published > 0
    
    def report(self, project_id: str = None) -> dict:
        """Generate project or platform report."""
        if project_id:
            project = self.projects.get(project_id)
            if not project:
                return {'error': 'Project not found'}
            return {
                'project': project.to_dict(),
                'pending_review': [
                    q for q in self.review_queue if q.startswith(project_id)
                ]
            }
        
        # Platform-level report
        stats = {'total_projects': len(self.projects), 'by_status': {}}
        for p in self.projects.values():
            stats['by_status'][p.status] = stats['by_status'].get(p.status, 0) + 1
        stats['pending_review'] = len(self.review_queue)
        stats['platform'] = self.platform.value
        return stats

# Demo
if __name__ == '__main__':
    engine = DramaEngine(DramaPlatform.DOUYIN)
    
    print("=== Domestic Drama Engine Demo ===\n")
    
    # Create a project
    project = engine.create_project(
        title='重生之都市修仙',
        genre=DramaGenre.FANTASY,
        total_episodes=10,
        description='现代都市修仙短剧'
    )
    print(f"Created project: {project.title}")
    
    # Add characters
    project.add_character('李逍遥', 'protagonist', '重生回都市的修仙者', 25)
    project.add_character('苏瑶', 'supporting', '女主角，医生', 23)
    
    # Create episodes
    ep1 = engine.create_episode(
        project.title,  # Using title as proxy for project_id
        1, '重生归来',
        '李逍遥从2099年重生回2026年，发现自己回到了大学时代...',
        120
    )
    print(f"Episode 1: {ep1.title} ({ep1.duration_sec}s)")
    
    # Check content
    result = engine.check_content(ep1.script)
    print(f"Content check: {result}")
    
    # Report
    report = engine.report()
    print(f"\nPlatform report: {json.dumps(report, ensure_ascii=False, indent=2)}")
