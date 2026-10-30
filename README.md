graph TD
    %% Clientes
    subgraph Clientes ["Clientes (Capa de Presentación)"]
        C1[Cliente Web]
        C2[Cliente Móvil]
    end

    %% Balanceador de Carga
    LB{{"Balanceador de Carga\n(Nginx / HAProxy)"}}

    %% Servidores / Workers
    subgraph Cluster ["Servidores Workers (Procesamiento)"]
        S1[Servidor 1\nPool de Hilos]
        S2[Servidor 2\nPool de Hilos]
        S3[Servidor N\nPool de Hilos]
    end

    %% Cola de Mensajes
    MQ>["Cola de Mensajes\n(RabbitMQ)"]

    %% Almacenamiento Distribuido
    subgraph Almacenamiento ["Almacenamiento Distribuido"]
        DB[(Base de Datos Relacional\nPostgreSQL)]
        S3_Obj[(Object Storage\nAmazon S3)]
    end

    %% Conexiones
    C1 -->|Peticiones HTTP/Sockets| LB
    C2 -->|Peticiones HTTP/Sockets| LB
    LB -->|Distribución de Carga| S1
    LB -->|Distribución de Carga| S2
    LB -->|Distribución de Carga| S3
    
    S1 <-->|Publica/Consume Eventos| MQ
    S2 <-->|Publica/Consume Eventos| MQ
    S3 <-->|Publica/Consume Eventos| MQ

    S1 -->|Lectura/Escritura| DB
    S2 -->|Lectura/Escritura| DB
    S3 -->|Lectura/Escritura| DB
    
    S1 -->|Archivos Estáticos/Multimedia| S3_Obj
    S2 -->|Archivos Estáticos/Multimedia| S3_Obj
    S3 -->|Archivos Estáticos/Multimedia| S3_Obj