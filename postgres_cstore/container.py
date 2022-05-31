from postgres_cstore.config import Config
from postgres_cstore.process import Process


class Container(object):
    """Container class.
    """
    def __init__(self, config: Config) -> None:
        """Initialize container.
        :param config: Configuration of postgres-cstore.
        """
        # Set an instance attribution as a delegation.
        self.config = config

    def run(self) -> str:
        """Run contailer from image.
        :return: str. The container is stored as an internal state.
        """
        cmd = "docker run \
               --name {name} \
               -p {port}:{port} \
               -e POSTGRES_USER={user} \
               -e POSTGRES_PASSWORD={password} \
               -v {volume} \
               -d {image}:{version}"
        # The docker run command returns a container id. But it can use the container name (self.name)
        # to start and stop the container etc. So It abandons the container id.
        _ = Process.run(cmd.format(
            name=self.config.name,
            image=self.config.image,
            version=self.config.version,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            volume=self.config.volume
        ))
        return self.config.name

    def start(self) -> str:
        """Start container.
        :return: str. The container is stored as an internal state.
        """
        cmd = "docker start {name}"
        return Process.run(cmd.format(name=self.config.name))

    def stop(self) -> str:
        """Stop container.
        :return: str. container_id. The container_id is stored as an internal state.
        """
        cmd = "docker stop {name}"
        return Process.run(cmd.format(name=self.config.name))

    def commit(self, image, version) -> (str, str):
        """Commit container.
        :param image: str. An image is a name committed to a docker image.
        :param version: str. A version is committed with the image.
        :return: (str, str). The image and version are committed as a docker image.
        """
        cmd = "docker commit {name} {image}:{version}"
        # The docker commit command returns an image id. But it can use the image name (image)
        # to run the image etc. So It abandons the image id.
        _ = Process.run(cmd.format(
            name=self.config.name,  # A container saved as an image is the current container.
            image=image,
            version=version,
        ))
        return image, version
