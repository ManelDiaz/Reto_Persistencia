# Reto-Persistencia

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
6. Por ultimo se decidió incluir pydantic para poder eliminar los datos disparejos que generaban que los gráficos no pudieran ser correctamente visualizables. 

Instrucciones de uso:
- Clonar el repositorio con el comando `git clone`.
- Levantar los contenedores ejecutando `docker-compose up -d` en la terminal de WSL.
- Buscando localhost:3000 e iniciando sesion con user: admin psw: admin y buscando en los dashboards es posible ver los datos almacenados en la db.
- Es posible acceder mediante linea de comandos a la base de datos mediante el siguiente comando en WSL: docker exec -it postgres_turbina psql -U postgres -d turbina_db
- Visualizar en el archivo .../app/logs/turbine_import.log si las insecciones de datos han sido correctas o no. 


Posibles vías de mejora:
- Añadir alertas en grafana en caso de que lleguen datos anómalos
- Utilizar Influxdb en vez de Postgres

Problemas encontrados:
- Al cargar los datos del csv en grafana se rompían los graficos debido a datos anómalos
- Al tener datos negativos en el csv, la subida a postgres eran rechazado lo que afectaba al análisis
- Problemas a la hora de mantener los dashboards de grafana una vez detenido el contendor de grafana.

Alternativas posibles:
- Utilizar FastAPI para probar los endpoints más fácilmente
- Automatizar el despliegue a github con CI/CD utilizando Github Actions para cada push
