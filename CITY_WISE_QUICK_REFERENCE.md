# City-Wise Filtering - Quick Reference

## TL;DR

All APIs now support optional city-wise filtering with `?city_id=X` parameter.

---

## API Endpoints

### Categories
```
GET /api/v1/categories              # All categories
GET /api/v1/categories?city_id=1    # City 1 categories
```

### Sub-Categories
```
GET /api/v1/sub-categories              # All sub-categories
GET /api/v1/sub-categories?city_id=1    # City 1 sub-categories
GET /api/v1/sub-categories/by-category/1              # Category 1 sub-categories
GET /api/v1/sub-categories/by-category/1?city_id=1    # Category 1 sub-categories in city 1
```

### Banners
```
GET /api/v1/banners              # All banners
GET /api/v1/banners?city_id=1    # City 1 banners
```

### Businesses
```
GET /api/v1/businesses              # All businesses
GET /api/v1/businesses?city_id=1    # City 1 businesses
```

---

## Quick Test

```bash
# Get all categories
curl "http://localhost:8000/api/v1/categories"

# Get city 1 categories
curl "http://localhost:8000/api/v1/categories?city_id=1"
```

---

## Frontend Usage

### JavaScript
```javascript
// All categories
fetch('/api/v1/categories')

// City 1 categories
fetch('/api/v1/categories?city_id=1')

// Dynamic city
const cityId = 1;
fetch(`/api/v1/categories?city_id=${cityId}`)
```

### React
```javascript
const [categories, setCategories] = useState([]);

useEffect(() => {
  const url = cityId 
    ? `/api/v1/categories?city_id=${cityId}`
    : '/api/v1/categories';
  
  fetch(url)
    .then(r => r.json())
    .then(d => setCategories(d.data || []));
}, [cityId]);
```

---

## Response Format

```json
{
  "response": true,
  "title": "Categories List",
  "data": [
    {
      "id": 1,
      "name": "Category Name",
      "city_id": 1,
      "created_at": "2024-05-27T10:00:00",
      "updated_at": "2024-05-27T10:00:00"
    }
  ],
  "message": null,
  "error": null
}
```

---

## Behavior

| Request | Response |
|---------|----------|
| No city_id | All records from all cities |
| city_id=1 | Only records with city_id=1 |
| city_id=999 | Empty list (no records) |

---

## Files Modified

### Models
- `db/models/category.py`
- `db/models/sub_category.py`
- `db/models/banner.py`
- `db/models/business.py`

### Repositories
- `repositories/category_repository.py`
- `repositories/sub_category_repository.py`
- `repositories/banner_repository.py`
- `repositories/business_repository.py`

### Services
- `services/category_service.py`
- `services/sub_category_service.py`
- `services/banner_service.py`
- `services/business_service.py`

### Routes
- `routers/routes/category.py`
- `routers/routes/sub_category.py`
- `routers/routes/banner.py`
- `routers/routes/business.py`

---

## Documentation

- `CITY_WISE_FILTERING_IMPLEMENTATION.md` - Full implementation details
- `CITY_WISE_API_TESTING_GUIDE.md` - Testing guide with examples
- `CITY_WISE_FILTERING_SUMMARY.md` - High-level overview
- `CITY_WISE_VERIFICATION_CHECKLIST.md` - Verification checklist
- `CITY_WISE_QUICK_REFERENCE.md` - This file

---

## Status

✅ **COMPLETE AND PRODUCTION READY**

- All APIs updated
- Database migrated
- Documentation complete
- Tested and verified

---

## Support

For detailed information, see:
1. CITY_WISE_FILTERING_IMPLEMENTATION.md
2. CITY_WISE_API_TESTING_GUIDE.md
3. CITY_WISE_FILTERING_SUMMARY.md

