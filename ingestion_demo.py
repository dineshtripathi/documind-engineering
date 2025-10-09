#!/usr/bin/env python3
"""
Vector Database Enrichment Demo
Shows how to populate DocuMind with diverse technical content
"""
import sys
sys.path.append('/home/dinesh/documind-engineering')

def demo_content_ingestion():
    """Demo content for populating vector database."""
    print("📚 DocuMind Vector Database Enrichment")
    print("=" * 50)

    # Sample content that could be crawled and ingested
    sample_contents = {
        "python_fastapi": {
            "title": "FastAPI Tutorial - Building Modern APIs",
            "content": """
FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

Key Features:
- Fast: Very high performance, on par with NodeJS and Go (thanks to Starlette and Pydantic)
- Fast to code: Increase the speed to develop features by about 200% to 300%
- Fewer bugs: Reduce about 40% of human (developer) induced errors
- Intuitive: Great editor support. Completion everywhere. Less time debugging
- Easy: Designed to be easy to use and learn. Less time reading docs
- Short: Minimize code duplication. Multiple features from each parameter declaration
- Robust: Get production-ready code. With automatic interactive documentation

Example API:
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

Automatic Documentation:
FastAPI automatically generates OpenAPI and JSON Schema documentation.
""",
            "domain": "technical",
            "source": "docs.python.org/fastapi"
        },

        "stack_overflow_async": {
            "title": "Understanding Python Async/Await",
            "content": """
Question: How to properly use async/await in Python?

Answer: Python's async/await syntax allows you to write asynchronous code that looks and feels like synchronous code.

Basic Example:
```python
import asyncio

async def fetch_data():
    # Simulate async operation
    await asyncio.sleep(1)
    return "Data fetched"

async def main():
    result = await fetch_data()
    print(result)

# Run the async function
asyncio.run(main())
```

Key Concepts:
1. async def: Declares an asynchronous function
2. await: Waits for an async operation to complete
3. asyncio.run(): Runs the main async function
4. Event Loop: Manages and executes async tasks

FastAPI Integration:
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/async-endpoint")
async def async_endpoint():
    data = await fetch_data()
    return {"result": data}
```

Best Practices:
- Use async for I/O-bound operations
- Don't use async for CPU-bound tasks
- Always await async functions
- Use asyncio for concurrent execution
""",
            "domain": "technical",
            "source": "stackoverflow.com"
        },

        "microsoft_dotnet": {
            "title": "ASP.NET Core Web API Development",
            "content": """
ASP.NET Core is a cross-platform, high-performance framework for building modern, cloud-enabled, Internet-connected apps.

Creating a Web API:
```csharp
[ApiController]
[Route("api/[controller]")]
public class WeatherForecastController : ControllerBase
{
    [HttpGet]
    public IEnumerable<WeatherForecast> Get()
    {
        return Enumerable.Range(1, 5).Select(index => new WeatherForecast
        {
            Date = DateTime.Now.AddDays(index),
            TemperatureC = Random.Shared.Next(-20, 55),
            Summary = Summaries[Random.Shared.Next(Summaries.Length)]
        })
        .ToArray();
    }
}
```

Dependency Injection:
```csharp
public void ConfigureServices(IServiceCollection services)
{
    services.AddControllers();
    services.AddScoped<IWeatherService, WeatherService>();
}
```

Entity Framework Integration:
```csharp
public class ApplicationDbContext : DbContext
{
    public DbSet<WeatherForecast> WeatherForecasts { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        optionsBuilder.UseSqlServer(connectionString);
    }
}
```

Features:
- Built-in dependency injection
- Configuration system
- Logging framework
- Health checks
- OpenAPI/Swagger integration
- Authentication and authorization
""",
            "domain": "technical",
            "source": "docs.microsoft.com"
        },

        "machine_learning": {
            "title": "Machine Learning with Python - Scikit-learn",
            "content": """
Scikit-learn is a powerful machine learning library for Python that provides simple and efficient tools for data mining and data analysis.

Classification Example:
```python
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
iris = datasets.load_iris()
X, y = iris.data, iris.target

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

# Train model
clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_train, y_train)

# Make predictions
predictions = clf.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Accuracy: {accuracy:.2f}")
```

Regression Example:
```python
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# Feature scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Linear regression
reg = LinearRegression()
reg.fit(X_scaled, y)
```

Model Pipeline:
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# Create pipeline
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('svm', SVC())
])

pipe.fit(X_train, y_train)
```

Key Algorithms:
- Supervised Learning: Classification, Regression
- Unsupervised Learning: Clustering, Dimensionality Reduction
- Model Selection: Cross-validation, Grid Search
- Preprocessing: Feature scaling, encoding
""",
            "domain": "technical",
            "source": "scikit-learn.org"
        }
    }

    print("📄 Sample Content for Vector Database:")
    print()

    for key, content in sample_contents.items():
        print(f"🔖 {content['title']}")
        print(f"   📍 Source: {content['source']}")
        print(f"   🏷️  Domain: {content['domain']}")
        print(f"   📊 Length: {len(content['content'])} characters")
        print(f"   📝 Preview: {content['content'][:150]}...")
        print()

    print("🚀 Ingestion Process:")
    print("1. Content extraction from websites")
    print("2. Domain classification (technical/finance/medical/etc)")
    print("3. Text chunking (220 tokens with 40 token overlap)")
    print("4. BGE-M3 embedding generation")
    print("5. Qdrant vector storage with metadata")
    print("6. Domain-aware retrieval ready")

    print()
    print("🎯 Benefits of Web Crawling:")
    print("• 📈 Diverse knowledge base")
    print("• 🔄 Up-to-date information")
    print("• 🎨 Domain-specific expertise")
    print("• 🔍 Enhanced search quality")
    print("• 💡 Better code generation")
    print("• 📚 Comprehensive documentation")

if __name__ == "__main__":
    demo_content_ingestion()
