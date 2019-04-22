FROM postgres:11
ARG USERNAME
ARG PASSWORD
ARG some_var
RUN echo "username: $USERNAME, password: $PASSWORD"
ENV POSTGRES_USER=${USERNAME} 
ENV POSTGRES_PASSWORD=${PASSWORD}
ENV POSTGRES_DB clickonly
ADD create_redirect_db.sql /docker-entrypoint-initdb.d/
