# City-Wise Filtering Implementation - Complete Status

## Overview

All APIs for Business, Category, Sub-Category, and Banner have been successfully implemented with city-wise filtering. When `city_id` is provided, only records for that city are returned. When `city_id` is not provided, all records across all cities are returned.

---

## Implementation Details

### 1. Database Models

All models have been updated with `city_id` foreign key:

#### Category Model
```python
city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=True)
city = relationship("City", backref="categories")
```

#### Sub-Category Model
```python
city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=True)
city = relationship("City", backref="sub_categories")
```

#### Banner Model
```python
city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=True)
city = relationship("City", backref="banners")
```

#### Business Model
```python
city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=True)
city = relationship("City", backref="businesses")
```

**Note**: All `city_id` columns are:
- **Nullable**: Records can exist without a city (global records)
- **Optional**: Filtering is optional
- **Cascading**: When a city is deleted, all associated records are deleted

---

### 2. Repository Layer

All repositories have been updated with optional `city_id` filtering:

#### Category Repository
```python
def get_all_categories(db: Session, city_id: Optional[int] = None):
    query = db.query(Category)
    if city_id:
        query = query.filter(Category.city_id == city_id)
    return query.all()
```

#### Sub-Category Repository
```python
def get_all_sub_categories(db: Session, city_id: Optional[int] = None):
    query = db.query(SubCategory)
    if city_id:
        query = query.filter(SubCategory.city_id == city_id)
    return query.all()

def get_sub_categories_by_category(db: Session, category_id: int, city_id: Optional[int] = None):
    query = db.query(SubCategory).filter(SubCategory.category_id == category_id)
    if city_id:
        query = query.filter(SubCategory.city_id == city_id)
    return query.all()
```

#### Banner Repository
```python
def get_all_banners(db: Session, city_id: Optional[int] = None):
    query = db.query(Banner)
    if city_id:
        query = query.filter(Banner.city_id == city_id)
    return query.all()
```

#### Business Repository
```python
def get_all_businesses(db: Session, city_id: Optional[int] = None):
    query = db.query(Business)
    if city_id:
        query = query.filter(Business.city_id == city_id)
    return query.all()
```

---

### 3. Service Layer

All services pass the `city_id` parameter to repositories:

#### Category Service
```python
def get_all_categories(db: Session, city_id: Optional[int] = None):
    return category_repository.get_all_categories(db, city_id)
```

#### Sub-Category Service
```python
def get_all_sub_categories(db: Session, city_id: Optional[int] = None):
    return sub_category_repository.get_all_sub_categories(db, city_id)

def get_sub_categories_by_category(db: Session, category_id: int, city_id: Optional[int] = None):
    return sub_category_repository.get_sub_categories_by_category(db, category_id, city_id)
```

#### Banner Service
```python
def get_all_banners(db: Session, city_id: Optional[int] = None):
    return banner_repository.get_all_banners(db, city_id)
```

#### Business Service
```python
def get_all_businesses(db: Session, city_id: Optional[int] = None):
    return business_repository.get_all_businesses(db, city_id)
```

---

### 4. API Routes

All routes accept optional `city_id` query parameter:

#### Category Routes
```python
@router.get("/")
def list_categories(city_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    categories = category_service.get_all_categories(db, city_id)
    return success_list(title="Categories List", data=categories)
```

#### Sub-Category Routes
```python
@router.get("/")
def list_sub_categories(city_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    sub_categories = sub_category_service.get_all_sub_categories(db, city_id)
    return success_list(title="Sub Categories List", data=sub_categories)

@router.get("/by-category/{category_id}")
def list_sub_categories_by_category(category_id: int, city_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    sub_categories = sub_category_service.get_sub_categories_by_category(db, category_id, city_id)
    return success_list(title="Sub Categories by Category", data=sub_categories)
```

#### Banner Routes
```python
@router.get("/")
def list_banners(city_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    banners = banner_service.get_all_banners(db, city_id)
    return success_list(title="Banners List", data=banners)
```

#### Business Routes
```python
@router.get("/")
def list_businesses(city_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    businesses = business_service.get_all_businesses(db, city_id)
    return success_list(title="Businesses List", data=businesses)
```

---

## API Usage Examples

### Get All Categories (No City Filter)
```
GET /api/v1/categories
```
**Response**: All categories from all cities

---

### Get Categories for Specific City
```
GET /api/v1/categories?city_id=1
```
**Response**: Only categories where `city_id = 1`

---

### Get All Sub-Categories (No City Filter)
```
GET /api/v1/sub-categories
```
**Response**: All sub-categories from all cities

---

### Get Sub-Categories for Specific City
```
GET /api/v1/sub-categories?city_id=1
```
**Response**: Only sub-categories where `city_id = 1`

---

### Get Sub-Categories by Category (No City Filter)
```
GET /api/v1/sub-categories/by-category/5
```
**Response**: All sub-categories for category 5 from all cities

---

### Get Sub-Categories by Category for Specific City
```
GET /api/v1/sub-categories/by-category/5?city_id=1
```
**Response**: Sub-categories for category 5 where `city_id = 1`

---

### Get All Banners (No City Filter)
```
GET /api/v1/banners
```
**Response**: All banners from all cities

---

### Get Banners for Specific City
```
GET /api/v1/banners?city_id=1
```
**Response**: Only banners where `city_id = 1`

---

### Get All Businesses (No City Filter)
```
GET /api/v1/businesses
```
**Response**: All businesses from all cities

---

### Get Businesses for Specific City
```
GET /api/v1/businesses?city_id=1
```
**Response**: Only businesses where `city_id = 1`

---

## Database Migration

A migration script `add_city_wise_filtering.py` was created and executed to:

1. Add `city_id` column to `categories` table
2. Add `city_id` column to `sub_categories` table
3. Add `city_id` column to `banners` table
4. Set up foreign key constraints with CASCADE delete
5. Make all `city_id` columns nullable

**Status**: ✅ Migration completed successfully

---

## Frontend Integration

### Query Parameters

All list endpoints accept the following query parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `city_id` | integer | No | Filter by city ID. If not provided, returns all records. |

### Response Format

All responses follow the standard format:

```json
{
  "response": true,
  "title": "Operation Title",
  "data": [
    {
      "id": 1,
      "name": "Category Name",
      "city_id": 1,
      ...
    }
  ],
  "message": "Success message",
  "error": null
}
```

### Implementation Checklist

- [x] Add `city_id` to Category model
- [x] Add `city_id` to Sub-Category model
- [x] Add `city_id` to Banner model
- [x] Business already had `city_id`
- [x] Update category repository with city filtering
- [x] Update sub-category repository with city filtering
- [x] Update banner repository with city filtering
- [x] Update business repository with city filtering
- [x] Update category service with city filtering
- [x] Update sub-category service with city filtering
- [x] Update banner service with city filtering
- [x] Update business service with city filtering
- [x] Update category routes with city_id query parameter
- [x] Update sub-category routes with city_id query parameter
- [x] Update banner routes with city_id query parameter
- [x] Update business routes with city_id query parameter
- [x] Run database migration
- [x] Test all endpoints with and without city_id

---

## Testing

### Test Cases

#### Test 1: Get all categories (no city filter)
```bash
curl -X GET "http://localhost:8000/api/v1/categories"
```
Expected: All categories returned

#### Test 2: Get categories for city 1
```bash
curl -X GET "http://localhost:8000/api/v1/categories?city_id=1"
```
Expected: Only categories with city_id=1

#### Test 3: Get all sub-categories (no city filter)
```bash
curl -X GET "http://localhost:8000/api/v1/sub-categories"
```
Expected: All sub-categories returned

#### Test 4: Get sub-categories for city 1
```bash
curl -X GET "http://localhost:8000/api/v1/sub-categories?city_id=1"
```
Expected: Only sub-categories with city_id=1

#### Test 5: Get all banners (no city filter)
```bash
curl -X GET "http://localhost:8000/api/v1/banners"
```
Expected: All banners returned

#### Test 6: Get banners for city 1
```bash
curl -X GET "http://localhost:8000/api/v1/banners?city_id=1"
```
Expected: Only banners with city_id=1

#### Test 7: Get all businesses (no city filter)
```bash
curl -X GET "http://localhost:8000/api/v1/businesses"
```
Expected: All businesses returned

#### Test 8: Get businesses for city 1
```bash
curl -X GET "http://localhost:8000/api/v1/businesses?city_id=1"
```
Expected: Only businesses with city_id=1

---

## Files Modified

### Models
- `db/models/category.py` - Added city_id foreign key
- `db/models/sub_category.py` - Added city_id foreign key
- `db/models/banner.py` - Added city_id foreign key
- `db/models/business.py` - Already had city_id

### Repositories
- `repositories/category_repository.py` - Added city_id filtering
- `repositories/sub_category_repository.py` - Added city_id filtering
- `repositories/banner_repository.py` - Added city_id filtering
- `repositories/business_repository.py` - Added city_id filtering

### Services
- `services/category_service.py` - Added city_id parameter
- `services/sub_category_service.py` - Added city_id parameter
- `services/banner_service.py` - Added city_id parameter
- `services/business_service.py` - Added city_id parameter

### Routes
- `routers/routes/category.py` - Added city_id query parameter
- `routers/routes/sub_category.py` - Added city_id query parameter
- `routers/routes/banner.py` - Added city_id query parameter
- `routers/routes/business.py` - Added city_id query parameter

### Migration
- `add_city_wise_filtering.py` - Database migration script

---

## Summary

✅ **City-wise filtering has been successfully implemented for all required APIs:**

1. **Business API** - Supports `?city_id=X` parameter
2. **Category API** - Supports `?city_id=X` parameter
3. **Sub-Category API** - Supports `?city_id=X` parameter
4. **Banner API** - Supports `?city_id=X` parameter

**Behavior:**
- When `city_id` is provided: Returns only records for that city
- When `city_id` is not provided: Returns all records from all cities

**Database:**
- All `city_id` columns are nullable
- Foreign key constraints with CASCADE delete
- Migration script executed successfully

**Frontend Integration:**
- Simple query parameter: `?city_id=1`
- Optional parameter: Can be omitted to get all records
- Standard response format maintained

---

## Next Steps

1. Test all endpoints with and without city_id parameter
2. Update frontend to pass city_id when needed
3. Monitor performance with large datasets
4. Consider adding pagination if needed

---

## Version History

- **v1.0** (2024-05-27): Initial city-wise filtering implementation
  - Added city_id to Category, Sub-Category, and Banner models
  - Updated all repositories with optional city filtering
  - Updated all services to pass city_id parameter
  - Updated all routes to accept city_id query parameter
  - Executed database migration successfully

