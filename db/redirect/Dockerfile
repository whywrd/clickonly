FROM postgres:11
ENV POSTGRES_USER ${REDIRECT_DB_USERNAME} 
ENV POSTGRES_PASSWORD ${REDIRECT_DB_PASSWORD} 
ENV POSTGRES_DB clickonly
ADD create_redirect_db.sql /docker-entrypoint-initdb.d/
