# City-Wise API Testing Guide

## Quick Test Commands

### 1. Get All Categories (No City Filter)
```bash
curl -X GET "http://localhost:8000/api/v1/categories"
```

### 2. Get Categories for City 1
```bash
curl -X GET "http://localhost:8000/api/v1/categories?city_id=1"
```

### 3. Get All Sub-Categories (No City Filter)
```bash
curl -X GET "http://localhost:8000/api/v1/sub-categories"
```

### 4. Get Sub-Categories for City 1
```bash
curl -X GET "http://localhost:8000/api/v1/sub-categories?city_id=1"
```

### 5. Get Sub-Categories by Category (No City Filter)
```bash
curl -X GET "http://localhost:8000/api/v1/sub-categories/by-category/1"
```

### 6. Get Sub-Categories by Category for City 1
```bash
curl -X GET "http://localhost:8000/api/v1/sub-categories/by-category/1?city_id=1"
```

### 7. Get All Banners (No City Filter)
```bash
curl -X GET "http://localhost:8000/api/v1/banners"
```

### 8. Get Banners for City 1
```bash
curl -X GET "http://localhost:8000/api/v1/banners?city_id=1"
```

### 9. Get All Businesses (No City Filter)
```bash
curl -X GET "http://localhost:8000/api/v1/businesses"
```

### 10. Get Businesses for City 1
```bash
curl -X GET "http://localhost:8000/api/v1/businesses?city_id=1"
```

---

## Expected Behavior

### Without city_id Parameter
- Returns all records from all cities
- Example: `GET /api/v1/categories` returns all categories

### With city_id Parameter
- Returns only records for that specific city
- Example: `GET /api/v1/categories?city_id=1` returns only categories with city_id=1

### Response Format
```json
{
  "response": true,
  "title": "Categories List",
  "data": [
    {
      "id": 1,
      "name": "Category Name",
      "description": "Description",
      "icon": "icon_url",
      "city_id": 1,
      "is_active": true,
      "created_at": "2024-05-27T10:00:00",
      "updated_at": "2024-05-27T10:00:00"
    }
  ],
  "message": null,
  "error": null
}
```

---

## Testing Checklist

### Categories API
- [ ] Test GET /categories (should return all categories)
- [ ] Test GET /categories?city_id=1 (should return only city 1 categories)
- [ ] Test GET /categories?city_id=2 (should return only city 2 categories)
- [ ] Test GET /categories?city_id=999 (should return empty list)

### Sub-Categories API
- [ ] Test GET /sub-categories (should return all sub-categories)
- [ ] Test GET /sub-categories?city_id=1 (should return only city 1 sub-categories)
- [ ] Test GET /sub-categories/by-category/1 (should return all sub-categories for category 1)
- [ ] Test GET /sub-categories/by-category/1?city_id=1 (should return city 1 sub-categories for category 1)

### Banners API
- [ ] Test GET /banners (should return all banners)
- [ ] Test GET /banners?city_id=1 (should return only city 1 banners)
- [ ] Test GET /banners?city_id=2 (should return only city 2 banners)

### Businesses API
- [ ] Test GET /businesses (should return all businesses)
- [ ] Test GET /businesses?city_id=1 (should return only city 1 businesses)
- [ ] Test GET /businesses?city_id=2 (should return only city 2 businesses)

---

## Postman Collection

### Import into Postman

Create a new collection with these requests:

#### 1. Get All Categories
- **Method**: GET
- **URL**: `{{base_url}}/api/v1/categories`

#### 2. Get Categories by City
- **Method**: GET
- **URL**: `{{base_url}}/api/v1/categories?city_id={{city_id}}`

#### 3. Get All Sub-Categories
- **Method**: GET
- **URL**: `{{base_url}}/api/v1/sub-categories`

#### 4. Get Sub-Categories by City
- **Method**: GET
- **URL**: `{{base_url}}/api/v1/sub-categories?city_id={{city_id}}`

#### 5. Get Sub-Categories by Category
- **Method**: GET
- **URL**: `{{base_url}}/api/v1/sub-categories/by-category/{{category_id}}`

#### 6. Get Sub-Categories by Category and City
- **Method**: GET
- **URL**: `{{base_url}}/api/v1/sub-categories/by-category/{{category_id}}?city_id={{city_id}}`

#### 7. Get All Banners
- **Method**: GET
- **URL**: `{{base_url}}/api/v1/banners`

#### 8. Get Banners by City
- **Method**: GET
- **URL**: `{{base_url}}/api/v1/banners?city_id={{city_id}}`

#### 9. Get All Businesses
- **Method**: GET
- **URL**: `{{base_url}}/api/v1/businesses`

#### 10. Get Businesses by City
- **Method**: GET
- **URL**: `{{base_url}}/api/v1/businesses?city_id={{city_id}}`

---

## Environment Variables for Postman

```json
{
  "base_url": "http://localhost:8000",
  "city_id": 1,
  "category_id": 1
}
```

---

## Frontend Integration Examples

### JavaScript/Fetch API

#### Get All Categories
```javascript
fetch('http://localhost:8000/api/v1/categories')
  .then(response => response.json())
  .then(data => console.log(data));
```

#### Get Categories for City 1
```javascript
fetch('http://localhost:8000/api/v1/categories?city_id=1')
  .then(response => response.json())
  .then(data => console.log(data));
```

#### Get Categories with Dynamic City ID
```javascript
const cityId = 1;
fetch(`http://localhost:8000/api/v1/categories?city_id=${cityId}`)
  .then(response => response.json())
  .then(data => console.log(data));
```

### React Example

```javascript
import { useState, useEffect } from 'react';

function CategoriesList({ cityId }) {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const url = cityId 
      ? `http://localhost:8000/api/v1/categories?city_id=${cityId}`
      : 'http://localhost:8000/api/v1/categories';
    
    fetch(url)
      .then(response => response.json())
      .then(data => {
        setCategories(data.data || []);
        setLoading(false);
      });
  }, [cityId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Categories {cityId ? `for City ${cityId}` : '(All Cities)'}</h2>
      <ul>
        {categories.map(category => (
          <li key={category.id}>{category.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

---

## Troubleshooting

### Issue: Empty Response
**Cause**: No records exist for the specified city
**Solution**: 
1. Verify city_id exists in the database
2. Verify records exist for that city
3. Try without city_id to see all records

### Issue: 404 Not Found
**Cause**: Endpoint doesn't exist
**Solution**: 
1. Check the endpoint URL
2. Verify the API is running
3. Check the port number

### Issue: 500 Server Error
**Cause**: Database connection issue
**Solution**:
1. Check database connection
2. Check .env file configuration
3. Check database migration status

---

## Performance Considerations

### Indexing
The `city_id` column is indexed for better query performance:
```sql
CREATE INDEX idx_categories_city_id ON categories(city_id);
CREATE INDEX idx_sub_categories_city_id ON sub_categories(city_id);
CREATE INDEX idx_banners_city_id ON banners(city_id);
CREATE INDEX idx_businesses_city_id ON businesses(city_id);
```

### Query Optimization
- Queries with city_id filter are optimized with indexes
- Queries without city_id return all records (may be slow with large datasets)
- Consider adding pagination for large result sets

---

## Next Steps

1. Test all endpoints with different city_id values
2. Verify response data includes city_id field
3. Test with invalid city_id (should return empty list)
4. Monitor query performance with large datasets
5. Consider adding pagination if needed

