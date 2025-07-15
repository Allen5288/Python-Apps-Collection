import re
from typing import Optional
from datetime import datetime, timezone


def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_strong_password(password: str) -> bool:
    """Check if password meets strength requirements"""
    if len(password) < 8:
        return False
    
    # At least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    
    # At least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    
    # At least one digit
    if not re.search(r'[0-9]', password):
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    sanitized = re.sub(r'[^\w\s-]', '', filename)
    # Replace spaces with underscores
    sanitized = re.sub(r'[-\s]+', '_', sanitized)
    return sanitized.strip('_')


def generate_slug(text: str, max_length: int = 50) -> str:
    """Generate URL-friendly slug from text"""
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    # Trim and limit length
    slug = slug.strip('-')[:max_length]
    return slug


def utc_now() -> datetime:
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse datetime string"""
    try:
        return datetime.strptime(dt_str, format_str)
    except ValueError:
        return None


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string with suffix"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def paginate_query(query, page: int = 1, per_page: int = 10):
    """Add pagination to SQLAlchemy query"""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }
