# Reto-Procesamiento

Miembros del equipo:
- Manel Díaz
- Rubén Alsasua
- Eneko Sáez

Enlace a GitHub: https://github.com/ManelDiaz/Reto_Persistencia

Pasos seguidos:
1. Para empezar creamos la base de datos de prostgres, ademas de levantar los contendores de Postgres y app.
2. A continuacion, se hizo la programacion básica para que su pudieran añadir los datos del csv a la base de datos.
3. Al acabar lo del paso anterior, se adaptó el codigo para que cambiara los timestamps del csv a la hora actual.
4. Además, realizamos las agregaciones
5. A continuacion, utilizamos grafana para monitorizar de una forma mas efectiva los diferentes datos.
6. Por ultimo se decidió incluir pydantic para poder eliminar los datos disparejos que generaban que los graficos no pudieran ser correctamente visualizables. 

Instrucciones de uso:
- Clonar el repositorio con el comando `git clone`.
- Levantar los contenedores ejecutando `docker-compose up -d` en la terminal de WSL.
- Buscando localhost:3000 e iniciando sesion con user: admin psw: admin y buscando en los dashboards es posible ver los datos almacenados en la db.
-  

Posibles vías de mejora:
- 

Problemas encontrados:
- 

Alternativas posibles:
- 
