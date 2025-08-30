# Supabase Migration Guide

This guide will help you migrate your AI Knowledge Base from PostgreSQL to Supabase.

## Prerequisites

1. Create a Supabase account at [supabase.com](https://supabase.com)
2. Create a new project in Supabase

## Step 1: Set up Supabase Database

1. Navigate to your Supabase project dashboard
2. Go to the SQL Editor
3. Run the migration script located at `supabase_migration.sql`
4. This will create all necessary tables, indexes, and Row Level Security policies

## Step 2: Update Environment Variables

1. Copy `.env.example` to `.env`
2. Update the following variables in your `.env` file:
   ```env
   SUPABASE_URL=your_supabase_project_url_here
   SUPABASE_KEY=your_supabase_anon_key_here
   ```

You can find these values in your Supabase project settings:
- **Project URL**: Settings → API → Project URL
- **Anon Key**: Settings → API → Project API keys → anon public

## Step 3: Install Dependencies

Run the following command to install the new dependencies:

```bash
pip install -r requirements.txt
```

## Step 4: Key Changes Made

### Database Connection
- Replaced SQLAlchemy with Supabase client
- Updated `app/core/database.py` to use Supabase
- Removed Alembic migrations (Supabase handles schema management)

### Models
- Converted SQLAlchemy models to Pydantic models
- All models now use UUID strings instead of UUID objects
- Removed SQLAlchemy relationships (handled by application logic)

### API Endpoints
- Updated all endpoints to use Supabase queries instead of SQLAlchemy
- Authentication and user management now use Supabase
- Updated security functions to work with Supabase

### Environment Variables
- `DATABASE_URL` → `SUPABASE_URL` and `SUPABASE_KEY`
- All other environment variables remain the same

## Step 5: Authentication Integration (Optional)

For enhanced security, you can integrate with Supabase Auth:

1. Enable authentication providers in your Supabase dashboard
2. Update the authentication logic to use Supabase Auth instead of custom JWT
3. This would eliminate the need for password hashing and JWT token management

## Step 6: Row Level Security

The migration includes Row Level Security (RLS) policies that ensure:
- Users can only access their own data
- Document chunks inherit permissions from their parent documents
- Chat messages inherit permissions from their parent sessions

## Testing the Migration

1. Start the application: `python start.py`
2. Test user registration and login
3. Test document upload and processing
4. Test chat functionality
5. Verify that users can only see their own data

## Rollback Plan

If you need to rollback to PostgreSQL:
1. Restore the previous version of the code from git
2. Ensure your PostgreSQL database is still available
3. Update environment variables back to PostgreSQL settings

## Benefits of Supabase

1. **Managed Database**: No need to manage PostgreSQL infrastructure
2. **Real-time**: Built-in real-time subscriptions
3. **Authentication**: Integrated auth system
4. **Storage**: Built-in file storage (can replace local file storage)
5. **API**: Auto-generated REST and GraphQL APIs
6. **Security**: Built-in Row Level Security
7. **Backups**: Automatic backups and point-in-time recovery

## Next Steps

1. Consider migrating file uploads to Supabase Storage
2. Implement real-time chat using Supabase subscriptions
3. Add social authentication providers
4. Set up automated backups and monitoring

## Support

If you encounter any issues during the migration:
1. Check the Supabase dashboard for error logs
2. Verify your environment variables are correct
3. Ensure the migration SQL script ran successfully
4. Check the application logs for specific error messages