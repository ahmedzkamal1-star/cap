try:
    from app import create_app
    app = create_app()
    print("Application created successfully!")
except Exception as e:
    import traceback
    traceback.print_exc()
