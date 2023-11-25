from abc import abstractmethod


class Protoble:
    """
    This class makes sure the extended class is able to represent as a protobuf object
    Which then can be used to transfer over a network
    """

    @abstractmethod
    def to_protobuf(self):
        """
        This method makes a protobuf object from this class

        :return: this class as protobuf object
        """
        return None
