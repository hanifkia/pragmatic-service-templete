mkdir -p .github/workflows docker docs migrations/versions scripts
mkdir -p tests/{unit/{test_services,test_models,test_utils},integration/{test_api,test_database,test_cache},e2e,fixtures}
mkdir -p src/{api/v1/endpoints,core/{services,models,interfaces},adapters/{database/{postgres,mongodb},cache,queue,storage,external},config,utils}
touch .dockerignore .env .env.example .gitignore docker-compose.yml LICENSE Makefile pyproject.toml pytest.ini README.md requirements.txt requirements-dev.txt setup.py .pre-commit-config.yaml
touch .github/workflows/{ci.yml,deploy.yml,tests.yml}
touch docker/{Dockerfile.dev,Dockerfile.prod,docker-compose.override.yml}
touch docs/{architecture.md,api.md,setup.md,deployment.md}
touch migrations/{alembic.ini,env.py,script.py.mako}
touch scripts/{init_db.py,seed_data.py,create_migration.sh,deploy.sh}
touch src/{main.py,api/{middleware.py,exceptions.py},core/{exceptions.py,validators.py},config/{settings.py,dependencies.py,logging.py},utils/{security.py,datetime.py,pagination.py,response.py},api/v1/{schemas.py,dependencies.py,router.py}}
touch tests/{unit/{test_services.py,test_models.py,test_utils.py},integration/{test_api.py,test_database.py,test_cache.py},e2e/test_api.py,fixtures/{test_user.py,test_product.py,test_order.py}}
