from src.app import create_app

app = create_app()

if __name__ == '__main__':
    import uvicorn
    from core.config import get_server_options

    print(get_server_options())
    uvicorn.run(
        'main:app',
        **get_server_options()
    )
