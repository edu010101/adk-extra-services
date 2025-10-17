# Artifacts

This library contains additional artifact services that complement the [standard artifact services](https://google.github.io/adk-docs/artifacts) available in the ADK ecosystem.


<div align="center">

```mermaid
graph TD
    A[BaseArtifactService] --> B[InMemoryArtifactService]
    A --> C[GcsArtifactService]
    A --> D[S3ArtifactService]
    A --> E[LocalFolderArtifactService]
    A --> F[SupabaseArtifactService]
    
    style A fill:#ffffff,stroke:#000000,stroke-width:1px,color:#000000
    style B fill:#f5f5f5,stroke:#666,stroke-width:1px,color:#000000
    style C fill:#f5f5f5,stroke:#666,stroke-width:1px,color:#000000
    style D fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000000
    style E fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000000
    style F fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000000
```

</div>

## S3ArtifactService

**Storage Mechanism:** Leverages AWS S3 or any S3-compatible storage (such as MinIO, DigitalOcean Spaces, Wasabi, Backblaze B2, and others) for persistent artifact storage. Each version of an artifact is stored as a separate object within the specified bucket.

**Object Naming Convention:** Constructs S3 object keys using a hierarchical path structure:
```
<app_name>/<user_id>/<session_id>/<filename>/<version>
```

### Key Features
- **Persistence:** Artifacts are stored durably in S3 or any S3-compatible backend, surviving application restarts and deployments.
- **Scalability:** Leverages the scalability, durability, and high availability of S3 and compatible providers.
- **Versioning:** Each save operation stores a new version as a distinct S3 object, enabling retrieval of specific artifact versions.
- **Compatibility:** Works with AWS S3, MinIO, DigitalOcean Spaces, Wasabi, Backblaze B2, and any provider compatible with [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html). You can also pass extra keyword arguments (`**kwargs`) to `S3ArtifactService` during initialization, which are forwarded directly to `boto3.client('s3', ...)` for advanced configuration (e.g., custom timeouts, SSL options, etc.).
- **Flexible Credentials:** Credentials can be provided explicitly or loaded from your environment (e.g., AWS environment variables, IAM roles, or local AWS config).

### Permissions Required
The application environment must have permissions to read from and write to the specified S3 bucket. For AWS, this typically means the IAM user or role must have `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`, and `s3:DeleteObject` permissions.

### Use Cases
- Production environments requiring persistent, scalable artifact storage.
- Scenarios where artifacts need to be shared across different application instances or services (by accessing the same S3 bucket).
- Applications needing long-term storage and retrieval of user or session data.
- Deployments on AWS, on-premises, or cloud providers supporting S3-compatible APIs.

### Instantiation

```python
from adk_extra_services.artifacts.s3_artifact_service import S3ArtifactService

bucket_name = "your-s3-bucket-name"  # Replace with your bucket name
endpoint_url = "https://s3.amazonaws.com"  # Or your S3-compatible endpoint (e.g., MinIO, AWS S3)

# Option 1: Use environment credentials (recommended for AWS setups)
s3_service = S3ArtifactService(
    bucket_name=bucket_name,
    endpoint_url=endpoint_url
)
print(f"S3ArtifactService initialized for bucket: {bucket_name}")
# Ensure your environment has credentials to access this bucket.
# e.g., via AWS environment variables, IAM roles, or config files

# Option 2: Pass explicit credentials
# s3_service = S3ArtifactService(
#     bucket_name=bucket_name,
#     endpoint_url=endpoint_url,
#     aws_access_key_id="YOUR_ACCESS_KEY",
#     aws_secret_access_key="YOUR_SECRET_KEY",
#     region_name="us-east-1"
# )

# Then pass it to the Runner
runner = Runner(..., artifact_service=s3_service)
```
---

### Example: Using MinIO

To run the example with MinIO:

1. **Start MinIO:**
   Make sure your MinIO server is running. You can use the following Docker command:
   ```bash
   docker run -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"
   ```

2. **Create the Bucket:**
   You must create the bucket you want to use (in this example, `test-bucket`) before running the script. You can do this via the MinIO web UI at [http://localhost:9001](http://localhost:9001) or with the MinIO client:
   ```bash
   mc alias set local http://localhost:9000 minioadmin minioadmin
   mc mb local/test-bucket
   ```
   *(If you don't have `mc` installed, you can download it from https://min.io/download#/mc)*

3. **Prepare your environment:**
   - `cd` into the `examples/artifacts` directory:
     ```bash
     cd examples/artifacts
     ```
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` to add your Google API key. For MinIO, you can keep the default credentials and endpoint as shown in the example.

4. **Run the example:**
   ```bash
   python s3_artifact_example.py
   ```

If everything is configured correctly, you should see a `.csv` file created in your MinIO bucket (`test-bucket`).

---

For a complete usage example, see [`s3_artifact_example.py`](./s3_artifact_example.py).

**Note:** This example is designed for MinIO or any S3-compatible storage and does not require AWS.

After MinIO is running and your bucket is created, you can run the example:

```bash
python s3_artifact_example.py
```

## SupabaseArtifactService

**Storage Mechanism:** Leverages Supabase Storage for persistent artifact storage, similar to S3. Each version of an artifact is stored as a separate object within the specified bucket.

**Object Naming Convention:** Constructs storage keys using a hierarchical path structure with a `public` prefix:
```
public/<app_name>/<user_id>/<session_id>/<filename>/<version>
```

### Key Features
- **Persistence:** Artifacts are stored durably in Supabase Storage, surviving application restarts and deployments.
- **Scalability:** Leverages the scalability and availability of Supabase's infrastructure built on top of cloud storage.
- **Versioning:** Each save operation stores a new version as a distinct object, enabling retrieval of specific artifact versions.
- **Free Tier:** Supabase offers a generous free tier, making it ideal for prototyping and smaller applications.
- **Easy Integration:** Works seamlessly with Supabase projects—just provide your project URL and API key.
- **Flexible Credentials:** Credentials can be provided explicitly or loaded from environment variables.

### Permissions Required
The Supabase storage bucket must have appropriate RLS (Row Level Security) policies configured. For basic usage with the `anon` key:
1. Create a storage bucket (e.g., `artifacts`)
2. Set up RLS policies to allow read/write access to objects with the `public/` prefix
3. Ensure your service role or anon key has the necessary permissions

### Use Cases
- Production environments with Supabase infrastructure
- Applications already using Supabase for other services (database, auth, etc.)
- Projects that want to avoid AWS and prefer an all-in-one platform
- Rapid prototyping with Supabase's free tier
- Applications needing persistent artifact storage with straightforward setup

### Instantiation

```python
from adk_extra_services.artifacts import SupabaseArtifactService

# Option 1: Use environment variables (recommended)
# Set SUPABASE_URL, SUPABASE_KEY, and optionally SUPABASE_BUCKET
supabase_service = SupabaseArtifactService()
print("SupabaseArtifactService initialized")

# Option 2: Pass explicit credentials
supabase_service = SupabaseArtifactService(
    url="https://your-project.supabase.co",
    key="your-anon-or-service-role-key",
    bucket_name="artifacts"  # defaults to 'artifacts'
)

# Then pass it to the Runner
runner = Runner(..., artifact_service=supabase_service)
```

### Example: Setting up Supabase Storage

1. **Create a Supabase Project:**
   - Go to [supabase.com](https://supabase.com) and create a new project
   - Note your project URL and anon/service role key

2. **Create Storage Bucket:**
   - In the Supabase dashboard, go to Storage
   - Create a new bucket called `artifacts` (or your preferred name)
   - Make it public or configure RLS policies as needed

3. **Configure RLS Policies (if using anon key):**
   ```sql
   -- Allow authenticated and anonymous users to upload/read/delete from public folder
   CREATE POLICY "Allow public folder access"
   ON storage.objects FOR ALL
   USING (bucket_id = 'artifacts' AND (storage.foldername(name))[1] = 'public');
   ```

4. **Prepare your environment:**
   - `cd` into the `examples/artifacts` directory:
     ```bash
     cd examples/artifacts
     ```
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` to add:
     ```
     SUPABASE_URL=https://your-project.supabase.co
     SUPABASE_KEY=your-anon-or-service-key
     SUPABASE_BUCKET=artifacts
     ```

5. **Install dependencies:**
   ```bash
   pip install supabase
   ```

6. **Run the example:**
   ```bash
   python supabase_artifact_example.py
   ```

If everything is configured correctly, you should see a `.csv` file created in your Supabase Storage bucket.

---

For a complete usage example, see [`supabase_artifact_example.py`](./supabase_artifact_example.py).

## LocalFolderArtifactService

**Storage Mechanism:** Saves artifacts on the local filesystem. Each artifact version is stored as a regular file under a directory structure:

```
<base_path>/<app_name>/<user_id>/<session_id>/<filename>/<version>
```

**Key Features**
- **Zero-setup:** No external services required—ideal for local development, unit tests, or small demos.
- **Versioning:** Same incremental versioning strategy as other services.
- **Isolation:** Works nicely with pytest temporary directories (`tmp_path`).

### Instantiation

```python
from adk_extra_services.artifacts import LocalFolderArtifactService

artifact_service = LocalFolderArtifactService(base_path="./artifacts_storage")
```

### Example: Using Local Storage

1. **Prepare your environment:**
   - `cd` into the `examples/artifacts` directory:
     ```bash
     cd examples/artifacts
     ```
   - Copy `.env.example` to `.env` (this file is shared with other examples):
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` to add your Google API key (the local example does **not** require any additional credentials).

2. **Run the example:**
   ```bash
   python local_folder_artifact_example.py
   ```

---

### Implementation Details

For implementation details, see [`adk_extra_services/artifacts`](../../src/adk_extra_services/artifacts/  ).