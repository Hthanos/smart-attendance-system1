# Registration Number Format

## Dedan Kimathi University of Technology

Registration numbers in this system follow the **Dedan Kimathi University of Technology** standard format:

```
E028-01-XXXX/YYYY
```

### Format Breakdown

- **E** - Faculty/School code (E = School of Engineering)
- **028** - Department code (028 = Electrical and Electronics Engineering)
- **01** - Program code
- **XXXX** - Sequential student number (4 digits)
- **YYYY** - Year of admission

### Examples

```
E028-01-1532/2022  - Sharon Yegon
E028-01-1278/2020  - Gidion Yegon
E028-01-1307/2020  - Gabriel Okal
```

## Implementation

### Validation

Registration numbers are validated using the following regex pattern:

```python
pattern = r'^E028-01-\d{4}/\d{4}$'
```

This is implemented in `src/utils/validators.py`:

```python
@staticmethod
def validate_registration_number(reg_number: str) -> bool:
    """Validate registration number format"""
    if not reg_number:
        return False
    
    # Example: E028-01-1532/2022
    pattern = r'^[A-Z]\d{3}-\d{2}-\d{4}/\d{4}$'
    return re.match(pattern, reg_number) is not None
```

### Directory Names

Since forward slashes (`/`) cannot be used in directory names, registration numbers are **sanitized** when creating directories:

**Original**: `E028-01-1532/2022`  
**Sanitized**: `E028-01-1532_2022` (slash replaced with underscore)

This is handled by helper functions in `src/utils/helpers.py`:

```python
# Convert for directory use
sanitized = Helpers.sanitize_reg_number("E028-01-1532/2022")
# Returns: "E028-01-1532_2022"

# Convert back to original format
original = Helpers.unsanitize_reg_number("E028-01-1532_2022")
# Returns: "E028-01-1532/2022"
```

### Face Images Storage

Face images are stored in directories named with sanitized registration numbers:

```
data/faces/
├── E028-01-1532_2022/
│   ├── face_001.jpg
│   ├── face_002.jpg
│   └── ...
├── E028-01-1278_2020/
│   ├── face_001.jpg
│   └── ...
```

### Database Storage

In the database, registration numbers are stored in their **original format** with the forward slash:

```sql
INSERT INTO students (registration_number, ...) 
VALUES ('E028-01-1532/2022', ...);
```

### Label Mapping

The face recognition model uses a label mapping file (`data/models/label_mapping.json`) that maps numeric labels to registration numbers:

```json
{
  "0": "E028-01-1532/2022",
  "1": "E028-01-1278/2020",
  "2": "E028-01-1307/2020"
}
```

## Usage in Application

### Student Registration

When registering a new student:

1. User enters registration number in format: `E028-01-1532/2022`
2. System validates format using `Validators.validate_registration_number()`
3. For face image storage, system sanitizes to: `E028-01-1532_2022`
4. Original format stored in database

### Sample Data Generation

The `scripts/populate_sample_data.py` script generates realistic registration numbers:

```python
def generate_registration_number(index, year=2022):
    """Generate realistic registration number - Moi University format"""
    # Format: E028-01-XXXX/YYYY (e.g., E028-01-1532/2022)
    return f"E028-01-{1000 + index:04d}/{year}"
```

This generates:
- `E028-01-1001/2022`
- `E028-01-1002/2022`
- `E028-01-1003/2022`
- etc.

## Configuration

The registration number pattern is defined in `.env.example`:

```bash
# Registration Number Format
# Format: E028-01-XXXX/YYYY
# Example: E028-01-1532/2022
REG_NUMBER_PATTERN="^E028-01-\d{4}/\d{4}$"
```

## Adapting to Other Institutions

If deploying this system at a different institution with a different format:

1. **Update Validation Pattern**  
   Edit `src/utils/validators.py` → `validate_registration_number()`

2. **Update Configuration**  
   Edit `.env.example` → `REG_NUMBER_PATTERN`

3. **Update Sample Data Generator**  
   Edit `scripts/populate_sample_data.py` → `generate_registration_number()`

4. **Update Documentation**  
   Update this file and relevant README files

### Example: Different Institution

For a format like `CS/2022/001`:

```python
# In validators.py
pattern = r'^[A-Z]{2}/\d{4}/\d{3}$'

# In populate_sample_data.py
def generate_registration_number(index, year=2022):
    return f"CS/{year}/{index:03d}"

# Sanitization already handles slashes → underscores
# CS/2022/001 becomes CS_2022_001
```

## Important Notes

⚠️ **Do not modify registration numbers after student enrollment**
- Face image directories are created based on registration numbers
- Changing a reg number requires moving face image directories
- Model must be retrained after such changes

✅ **Always use helper functions for directory operations**
```python
from src.utils.helpers import Helpers

# Creating face directory
reg_number = "E028-01-1532/2022"
safe_name = Helpers.sanitize_reg_number(reg_number)
face_dir = f"data/faces/{safe_name}"
```

✅ **Database queries use original format**
```python
# Correct
cursor.execute("SELECT * FROM students WHERE registration_number = ?", 
               ("E028-01-1532/2022",))

# Don't use sanitized version in database
```

## Testing

Test registration number handling:

```bash
# Run validator tests
pytest tests/test_services.py -k "registration"

# Test with sample data
python scripts/populate_sample_data.py
```

## Related Files

- **Validation**: `src/utils/validators.py`
- **Helpers**: `src/utils/helpers.py`
- **Configuration**: `.env.example`
- **Sample Data**: `scripts/populate_sample_data.py`
- **Database Schema**: `src/database/schema.sql`
