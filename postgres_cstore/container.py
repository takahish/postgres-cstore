import configparser
from postgres_cstore.process import Process

# Load configurations
config = configparser.ConfigParser()
config.read('conf/system.ini')


class Container(object):
    """Container class.
    """
    def __init__(self,
                 name=None, image=None, version=None, volume=None,  # Container settings.
                 user=None, password=None, port=None  # Connection settings.
                 ) -> None:
        """Initialize container.
        :param name: str. A container is created from a docker image specified by an image argument.
        :param image: str. An image is based by a container.
        :param version: str. It is a version of a docker image specified by an image argument.
        :param volume: str. It is a volume of a container.
        :param user: str. It is a user of postgres-cstore.
        :param password: str. It is password of a user.
        :param port: str. A port is used by postgres-cstore.
        """
        # Set container settings.
        self.name = name if name is not None else config.get('CONTAINER', 'name')
        self.image = image if image is not None else config.get('CONTAINER', 'image')
        self.version = version if version is not None else config.get('CONTAINER', 'version')
        self.volume = volume if volume is not None else config.get('CONTAINER', 'volume')

        # Set connection settings.
        self.port = port if port is not None else config.get('CONNECTION', 'port')
        self.user = user if user is not None else config.get('CONNECTION', 'user')
        self.password = password if password is not None else config.get('CONNECTION', 'password')

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
            name=self.name,
            image=self.image,
            version=self.version,
            port=self.port,
            user=self.user,
            password=self.password,
            volume=self.volume
        ))
        return self.name

    def start(self) -> str:
        """Start container.
        :return: str. The container is stored as an internal state.
        """
        cmd = "docker start {name}"
        return Process.run(cmd.format(name=self.name))

    def stop(self) -> str:
        """Stop container.
        :return: str. container_id. The container_id is stored as an internal state.
        """
        cmd = "docker stop {name}"
        return Process.run(cmd.format(name=self.name))

    def commit(self, image, version) -> (str, str):
        """Commit container.
        :param image: str. An image is a name committed to a docker image.
        :param version: str. A version is committed with the image.
        :return: (str, str). The image and version are committed as a docker image.
        """
        cmd = "docker commit {container_id} {image}:{version}"
        # The docker commit command returns an image id. But it can use the image name (image)
        # to run the image etc. So It abandons the image id.
        _ = Process.run(cmd.format(
            container_id=self.container_id if self.container_id is not None else self.name,
            image=image,
            version=version,
        ))
        return image, version
