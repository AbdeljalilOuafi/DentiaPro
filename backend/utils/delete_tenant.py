from django.db import connection

def delete_tenant_raw_sql(schema_name):
    try:
        print(f"Starting cleanup for orphaned tenant: {schema_name}")
        
        with connection.cursor() as cursor:
            cursor.execute("BEGIN;")
            
            cursor.execute(
                "SELECT id FROM public.tenants_tenant WHERE schema_name = %s",
                [schema_name]
            )
            tenant_id_result = cursor.fetchone()
            
            if not tenant_id_result:
                print(f"No tenant found with schema_name {schema_name}")
                cursor.execute("ROLLBACK;")
                return
                
            tenant_id = tenant_id_result[0]
            print(f"Found tenant with ID: {tenant_id}")
            
            cursor.execute(
                "SELECT id FROM public.users_user WHERE tenant_id = %s",
                [tenant_id]
            )
            user_ids = [row[0] for row in cursor.fetchall()]
            print(f"Found {len(user_ids)} users to delete")
            
            if user_ids:
                cursor.execute(
                    "DELETE FROM public.users_onetimepassword WHERE user_id IN %s",
                    [tuple(user_ids) if len(user_ids) > 1 else f"({user_ids[0]})"]
                )
                print("Deleted one-time passwords")
                
                # Delete user permissions
                cursor.execute(
                    "DELETE FROM public.users_user_user_permissions WHERE user_id IN %s",
                    [tuple(user_ids) if len(user_ids) > 1 else f"({user_ids[0]})"]
                )
                print("Deleted user permissions")
                
                # Delete user group relationships
                cursor.execute(
                    "DELETE FROM public.users_user_groups WHERE user_id IN %s",
                    [tuple(user_ids) if len(user_ids) > 1 else f"({user_ids[0]})"]
                )
                print("Deleted user group relationships")
                
                # Delete user profiles
                cursor.execute(
                    "DELETE FROM public.users_profile WHERE user_id IN %s",
                    [tuple(user_ids) if len(user_ids) > 1 else f"({user_ids[0]})"]
                )
                print("Deleted user profiles")
                
                # Delete users linked to this tenant
                cursor.execute(
                    "DELETE FROM public.users_user WHERE tenant_id = %s",
                    [tenant_id]
                )
                print(f"Deleted users for tenant ID {tenant_id}")
            
            # Delete domain
            cursor.execute(
                "DELETE FROM public.tenants_domain WHERE tenant_id = %s",
                [tenant_id]
            )
            print(f"Deleted domain records for tenant ID {tenant_id}")
            
            # Delete tenant
            cursor.execute(
                "DELETE FROM public.tenants_tenant WHERE id = %s",
                [tenant_id]
            )
            print(f"Deleted tenant record with ID {tenant_id}")
            
            # Commit the transaction if everything succeeded
            cursor.execute("COMMIT;")
            
        print("Cleanup completed successfully!")
        
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
        # Explicitly rollback the transaction on error
        with connection.cursor() as cursor:
            cursor.execute("ROLLBACK;")
        print("Transaction rolled back due to error")