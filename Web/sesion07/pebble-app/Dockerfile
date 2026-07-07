FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /src
COPY pom.xml .
COPY src ./src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /src/target/pebble-lab.jar /app/pebble-lab.jar
RUN printf 'FLAG{A_PEBBLE_RUNTIME_EXECUTION}\n' > /flag_profesor_pebble.txt \
    && printf 'FLAG{B_PEBBLE_RUNTIME_EXECUTION}\n' > /flag_alumno_pebble.txt
EXPOSE 7000
CMD ["java", "-jar", "/app/pebble-lab.jar"]
