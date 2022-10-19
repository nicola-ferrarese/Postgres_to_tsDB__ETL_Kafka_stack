## Change data capture template

this will create a Kafka stack along with two empty databases, one vanilla Postgres and one with Timescale pre-installed

### Installation

- run docker-compose to create the stack: 
```shell
docker-compose up --force-recreate
``` 
- apply the migrations, this will create hypertables and continuous aggregates in the destination database 
```python 
python3 manage.py migrate 
 ```

- create and populate the source database
  - *note:* Auth_token obtained via ilcsCloud, should be in the format ***"Bearer xxxxxxxxxxxxxx"***
    - if Auth_token not provided or wrong, the tables will still be created and the stack tested but records have to be inserted manually
```python
python3 import_data.py "<Auth_token>"
```

- Open Postman or any API tool
- **POST http://localhost:8083/connectors/** to create *Source Connector*:
```json
{
   "name": "env_snsr_source_connect",
   "config": {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "database.hostname": "source_db",
        "database.port": "5600",
        "database.user": "postgres",
        "database.password": "postgres",
        "database.dbname" : "postgres",
        "database.server.name": "postgres",
        "plugin.name": "pgoutput",

        "key.converter": "io.confluent.connect.avro.AvroConverter",
        "key.converter.schema.registry.url": "http://schemaregistry:8081",
        "value.converter": "io.confluent.connect.avro.AvroConverter",
        "value.converter.schema.registry.url": "http://schemaregistry:8081",
        

        "transforms": "route",
        "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
        "transforms.route.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
        "transforms.route.replacement": "$3",

        "time.precision.mode":"connect",
       
        "table.include.list": "public.env_measure"
   }
 }      
```
- **POST http://localhost:8083/connectors/** to create *Sink Connector*:
```json
{
    "name": "env_snsr_sink_connect",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
        "task.max": "1",
        "topics": "env_measure",
        "key.converter": "io.confluent.connect.avro.AvroConverter",
        "key.converter.schema.registry.url": "http://schemaregistry:8081",
        "value.converter": "io.confluent.connect.avro.AvroConverter",
        "value.converter.schema.registry.url": "http://schemaregistry:8081",
        "transforms": "unwrap",

        "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
        "connection.url": "jdbc:postgresql://destination_db:5500/postgres?verifyServerCertificate=false&useSSL=true&requireSSL=true",
        "connection.user": "postgres",
        "connection.password": "postgres",
        "batch.size": "2",
        "table.name.format": "postgres.public.envsensor_env_measure",
        "time.precision.mode":"connect",
        "insert.mode": "upsert",
        "pk.fields": "timestamp,id",
        "pk.mode": "record_value",
        "auto.create" : "false"
     
    }   
}
```

- By inspecting the timescale istance (localhost:5500) the table "env_measure" and the view "envsensor_view_30min" should be populated
- To check the status of the Kafka stack, access http://localhost:8888 

- In the left bar
  - Select topic to see all the messages being sent via Kafka inside env-measure topic
  - Select "kafka connect" to see connectors status and options

- From now on, every record Inserted or Updated in the source database will be replicated in the Sink database


