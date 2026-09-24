# domestic-drama - Domestic Short Drama Engine

Short drama engine optimized for Douyin and Kuaishou platforms.

## Features

- **Platform-Specific Rules**: Duration limits, content categories, sensitive word checks
- **Project Management**: Characters, episodes, scripts, status tracking
- **Content Review**: Automated content compliance checking
- **Vertical Format**: 9:16 aspect ratio support
- **Episode Pipeline**: Draft → Review → Published workflow

## Quick Start

```bash
python drama_engine.py
```

## Usage

```python
from drama_engine import DramaEngine, DramaGenre, DramaPlatform, DramaProject

# Create engine for Douyin
engine = DramaEngine(DramaPlatform.DOUYIN)

# Create a drama project
project = engine.create_project(
    title='重生之都市修仙',
    genre=DramaGenre.FANTASY,
    total_episodes=10,
    description='现代都市修仙短剧'
)

# Add characters
project.add_character('李逍遥', 'protagonist', '重生回都市的修仙者', 25)

# Create episodes
ep1 = engine.create_episode(
    project_id='abc12345',  # actual project ID
    ep_num=1,
    title='重生归来',
    script='李逍遥从2099年重生回2026年...',
    duration=120
)

# Check content compliance
result = engine.check_content(ep1.script)
print(f"Compliance: {result['passed']}")

# Submit for review
engine.submit_for_review('abc12345')

# Publish
engine.publish('abc12345')

# Get report
report = engine.report()
print(report)
```

## Platform Rules

| Rule | Douyin | Kuaishou |
|------|--------|----------|
| Min duration | 15s | 15s |
| Max duration | 300s | 180s |
| Max episodes | 100 | 50 |
| Aspect ratio | 9:16 | 9:16 |
| Content categories | Romance, Comedy, Family, Workplace | Romance, Comedy, Family, Revenge |

## Notes

- This is a content management engine, not a video generation tool
- For actual video production, integrate with ComfyUI / Wan2.1 / Kling
- Content review is rule-based; production use requires human review
- Sensitive word list is a starting point - customize per platform policies

## License

MIT
