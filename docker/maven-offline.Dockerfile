FROM maven:3.9.6-eclipse-temurin-17

# Build a small image with the project's declared dependencies downloaded into the image
# so subsequent test runs using this image don't need to re-download everything.
WORKDIR /tmp

# Copy only the pom so dependency:go-offline can resolve dependencies during image build
COPY servicio-banco-lp1/pom.xml /tmp/pom.xml

# Download dependencies into the image's local Maven repository
RUN mvn -B -f /tmp/pom.xml dependency:go-offline

CMD ["bash"]
