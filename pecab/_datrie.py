# https://github.com/hyunwoongko/pydatrie
from typing import List, Any, Dict


class _Node:
    code: int = None
    depth: int = None
    left: int = None
    right: int = None

    def __str__(self):
        return f"Node(code={self.code}, depth={self.depth}, left={self.left}, right={self.right})"

    def __repr__(self):
        return self.__str__()


class DoubleArrayTrie:
    _unit_size: int = 8
    _check: List[int]
    _base: List[int]
    _used: List[bool]

    _size: int
    _alloc_size: int
    _key: List[str]
    _key_size: int
    _value: List[int]
    _value_names: List[str]
    _progress: int
    _next_check_pos: int
    _error: int

    def __init__(self, data: Dict[str, Any]):
        self._check = None
        self._base = None
        self._used = None
        self._key = None
        self._size = 0
        self._alloc_size = 0
        self._error = 0
        self._value_names = [
            "surface",
            "left_id",
            "right_id",
            "word_cost",
            "POS",
            "POS_type",
            "morphemes",
        ]

        if data is not None and isinstance(data, dict):
            if len(data) > 0:
                self._build(data)
        else:
            raise ValueError("constructor param `data` is not a dictionary.")

        del self._used
        del self._key

    def _build(self, dictionary: Dict[str, Any]) -> int:
        dictionary = dict(sorted(dictionary.items(), key=lambda x: x[0]))
        self._value: List[Any] = list(dictionary.values())
        self._key: List[str] = list(dictionary.keys())
        self._key_size = len(self._key)
        self._progress = 0

        self._resize(65536 * 32)
        self._base[0] = 1
        self._next_check_pos = 0

        root_node = _Node()
        root_node.left = 0
        root_node.right = self._key_size
        root_node.depth = 0

        siblings: List[_Node] = []
        self._fetch(root_node, siblings)
        self._insert(siblings)
        return self._error

    def _resize(self, new_size: int) -> int:
        new_base: List[int] = [0] * new_size
        new_check: List[int] = [0] * new_size
        new_used: List[bool] = [False] * new_size

        if self._alloc_size > 0:
            new_base[: self._alloc_size] = self._base[: self._alloc_size]
            new_check[: self._alloc_size] = self._check[: self._alloc_size]
            new_used[: self._alloc_size] = self._used[: self._alloc_size]

        self._base = new_base
        self._check = new_check
        self._used = new_used
        self._alloc_size = new_size
        return self._alloc_size

    def _fetch(self, parent: _Node, siblings: List[_Node]) -> int:
        if self._error < 0:
            return 0

        prev = 0
        for i in range(parent.left, parent.right):
            if len(self._key[i]) < parent.depth:
                continue

            tmp: str = self._key[i]
            cur: int = 0

            if len(tmp) != parent.depth:
                cur = ord(tmp[parent.depth]) + 1

            if prev > cur:
                self._error = -3
                return 0

            if cur != prev or len(siblings) == 0:
                tmp_node = _Node()
                tmp_node.depth = parent.depth + 1
                tmp_node.code = cur
                tmp_node.left = i

                if len(siblings) != 0:
                    siblings[len(siblings) - 1].right = i

                siblings.append(tmp_node)

            prev = cur

        if len(siblings) != 0:
            siblings[len(siblings) - 1].right = parent.right

        return len(siblings)

    def _insert(self, siblings: List[_Node]) -> int:
        if self._error < 0:
            return 0

        begin: int = 0
        pos = max(siblings[0].code + 1, self._next_check_pos) - 1
        nonzero_num = 0
        first = 0

        if self._alloc_size <= pos:
            self._resize(pos + 1)

        while True:
            pos += 1

            if self._alloc_size <= pos:
                self._resize(pos + 1)

            if self._check[pos] not in [0, None]:
                nonzero_num += 1
                continue

            elif first == 0:
                self._next_check_pos = pos
                first = 1

            begin = pos - siblings[0].code
            if self._alloc_size <= (begin + siblings[len(siblings) - 1].code):
                l: float = (
                    1.05
                    if (1.05 > 1.0 * self._key_size / (self._progress + 1))
                    else 1.0 * self._key_size / (self._progress + 1)
                )
                self._resize(int(self._alloc_size * l))

            if self._used[begin]:
                continue

            outer_continue = False
            for i in range(1, len(siblings)):
                if self._check[begin + siblings[i].code] != 0:
                    outer_continue = True
                    break
            if outer_continue:
                continue

            break

        if 1.0 * nonzero_num / (pos - self._next_check_pos + 1) >= 0.95:
            self._next_check_pos = pos

        self._used[begin] = True
        self._size = (
            self._size
            if self._size > begin + siblings[len(siblings) - 1].code + 1
            else begin + siblings[len(siblings) - 1].code + 1
        )

        for i in range(len(siblings)):
            self._check[begin + siblings[i].code] = begin

        for i in range(len(siblings)):
            new_siblings: List[_Node] = []
            if self._fetch(siblings[i], new_siblings) == 0:
                self._base[begin + siblings[i].code] = -siblings[i].left - 1
                self._progress += 1
            else:
                h: int = self._insert(new_siblings)
                self._base[begin + siblings[i].code] = h
        return begin

    def _exact_match_search(self, key: str):
        _len = len(key)
        result: int = -1
        b: int = 1
        p: int

        for i in range(_len):
            p = b + ord(key[i]) + 1
            check = self._check[p].as_py()
            if b == check:
                b = self._base[p].as_py()
            else:
                return result

        p = b
        n = self._base[p].as_py()
        if b == self._check[p].as_py() and n < 0:
            result = -n - 1
        return result

    def _get_value_from_table(self, idx):
        return {value: self._value[value][idx].as_py() for value in self._value_names}

    def __getitem__(self, key: str):
        idx = self._exact_match_search(key)
        if idx >= 0:
            return self._get_value_from_table(idx)
        return None

    @classmethod
    def from_files(cls, arrays, words):
        trie = cls({})
        trie._base = arrays["base"]
        trie._check = arrays["check"]
        trie._value = words
        return trie
