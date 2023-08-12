from bigtree import Node


class DirectoryInfosNode(Node):
    """
    Custom Node to carry additional directory informations as Node attributes.
    """
    def __init__(self, name, filepath=None, total_files=0, total_filesize=0, **kwargs):
        super().__init__(name, **kwargs)
        self._filepath = filepath
        self.total_files = total_files
        self.total_filesize = total_filesize

    @property
    def filepath(self):
        if self._filepath:
            return self._filepath

        return "/".join([""] + [v.node_name for v in self.node_path])

    @property
    def recursive_files(self):
        if self.is_leaf:
            return self.total_files
        return (
            self.total_files + sum([child.recursive_files for child in self.children])
        )

    @property
    def recursive_filesize(self):
        if self.is_leaf:
            return self.total_filesize

        return (
            self.total_filesize +
            sum([child.recursive_filesize for child in self.children])
        )
