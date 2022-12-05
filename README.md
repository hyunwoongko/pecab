# Pecab
Pecab is pure python Korean morpheme analyzer based on [Mecab](https://github.com/taku910/mecab).
Mecab is a CRF-based morpheme analyzer made by Taku Kudo at 2011. It is very fast and accurate at the same time, which is why it is still very popular even though it is quite old.
However, it is known to be one of the most tricky libraries to install, and in fact many people have had a hard time installing Mecab.

So, since a few years ago, I wanted to make a pure python version of Mecab that was easy to install while inheriting the advantages of Mecab.
Now, Pecab came out. This ensures results very similar to Mecab and at the same time easy to install.
For more details, please refer the following.

## 1. Installation
```console
pip install pecab
```

## 2. Usages
The user API of Pecab is inspired by [KoNLPy](https://github.com/konlpy/konlpy), 
a one of the most famous natural language processing package in South Korea.

#### 1) `PeCab()`: creating Pecab object.
```python
from pecab import PeCab

pecab = PeCab()
```

#### 2) `morphs(text)`: splits text into morphemes.
```python
pecab.morphs("아버지가방에들어가시다")
['아버지', '가', '방', '에', '들어가', '시', '다']
```

#### 3) `pos(text)`: returns morphemes and POS tags together.
```python
pecab.pos("이것은 문장입니다.🧡")
[('이것', 'NP'), ('은', 'JX'), ('문장', 'NNG'), ('입니다', 'VCP+EF'), ('.', 'SF'), ('🧡', 'SY')]
```

#### 4) `nouns(text)`: returns all nouns in the input text.
```python
pecab.nouns("자장면을 먹을까? 짬뽕을 먹을까? 그것이 고민이로다.")
["자장면", "짬뽕", "그것", "고민"]
```

#### 5) `Pecab(user_dict=List[str])`: Set up a user dictionary.
Note that words included in the user dictionary **cannot contain spaces**.
- Without `user_dict`
```python
from pecab import PeCab

pecab = PeCab()
pecab.pos("저는 삼성디지털프라자에서 지펠냉장고를 샀어요.")
[('저', 'NP'), ('는', 'JX'), ('삼성', 'NNP'), ('디지털', 'NNP'), ('프라자', 'NNP'), ('에서', 'JKB'), ('지', 'NNP'), ('펠', 'NNP'), ('냉장고', 'NNG'), ('를', 'JKO'), ('샀', 'VV+EP'), ('어요', 'EF'), ('.', 'SF')]
```
- With `user_dict`
```python
from pecab import PeCab

user_dict = ["삼성디지털프라자", "지펠냉장고"]
pecab = PeCab(user_dict=user_dict)
pecab.pos("저는 삼성디지털프라자에서 지펠냉장고를 샀어요.")
[('저', 'NP'), ('는', 'JX'), ('삼성디지털프라자', 'NNG'), ('에서', 'JKB'), ('지펠냉장고', 'NNG'), ('를', 'JKO'), ('샀', 'VV+EP'), ('어요', 'EF'), ('.', 'SF')]
```

#### 6) `PeCab(split_compound=bool)`: Divide compound words into smaller pieces.
```python
from pecab import PeCab

pecab = PeCab(split_compound=True)
pecab.morphs("가벼운 냉장고를 샀어요.")
['가볍', 'ᆫ', '냉장', '고', '를', '사', 'ㅏㅆ', '어요', '.']
```

#### 7) `ANY_PECAB_FUNCTION(text, drop_space=bool)`: Determines whether spaces are returned or not.
This can be used for all of `morphs`, `pos`, `nouns`. default value of this is `True`.
```python
from pecab import PeCab

pecab = PeCab()
pecab.pos("토끼정에서 크림 우동을 시켰어요.")
[('토끼', 'NNG'), ('정', 'NNG'), ('에서', 'JKB'), ('크림', 'NNG'), ('우동', 'NNG'), ('을', 'JKO'), ('시켰', 'VV+EP'), ('어요', 'EF'), ('.', 'SF')]

pecab.pos("토끼정에서 크림 우동을 시켰어요.", drop_space=False)
[('토끼', 'NNG'), ('정', 'NNG'), ('에서', 'JKB'), (' ', 'SP'), ('크림', 'NNG'), (' ', 'SP'), ('우동', 'NNG'), ('을', 'JKO'), (' ', 'SP'), ('시켰', 'VV+EP'), ('어요', 'EF'), ('.', 'SF')]
```

## 3. Implementation Details
In fact, there was a pure python Korean morpheme analyzer before. 
Its name is [Pynori](https://github.com/gritmind/python-nori).
I've been using Pynori well, and a big thank you to the developer of Pynori. 
However, Pynori had some problems that needed improvement. 
So I started making Pecab with its codebase and I focused on solving these problems.

### 1) 50 ~ 100 times faster loading and less memory usages
When we create Pynori object, it reads matrix and vocabulary files from disk and makes a Trie in runtime. 
However, this is quite a heavy task. In fact, when I run Pynori for the first time, my computer freezes for almost 10 seconds. 
So I solved this with the two key ideas: **1) zero-copy memory mapping** and **2) double array trie system**.

The first key idea was **zero copy memory mapping**.
This allows data in virtual memory (disk) to be used as-is without copying almost to memory. 
In fact, Pynori takes close to 5 seconds to load `mecab_csv.pkl` file to memory, and this comes with a very heavy burden.
I designed the matrix file to be saved using `numpy.memmap` and the vocabulary using memmapable `pyarrow.Table`, 

However, there was one problem with designing this.
The Trie data structure which was used in Pynori is quite difficult to store in memmap form.
In fact, numpy only supports arrays and matrices well, and pyarrow only supports tables in most cases. 
Therefore, I initially wanted to use a table form instead of a trie. 
However, Table has a linear time complexity of O(n) to index a particular key, 
so the searching time could be actually very longer than before. 
So the second key idea was **Double Array Trie (DATrie)**.
The Double Array Trie that can be saved in memmap files easily, so it was one of the best option for me.
I wanted to implement everything in Python to facilitate package installation, but unfortunately I couldn't find the DATrie source code implemented in pure python. 
So I made it myself, and you can find the implementation [here](https://github.com/hyunwoongko/pydatrie).
DATrie has only two simple integer arrays (base, check) instead of a complex node-based structure unlike general tries, 
and all keys can be easily retrieved with them. And these two arrays are super easy to make with memmap !

In conclusion, it took almost 50 ~ 100 times less time than before to read these two files,
and memory consumption was also significantly reduced because they did not actually reside in memory.

### 2) User-friendly and Pythonic API
Another difficulty I had while using Pynori was the User API. 
It has a fairly Java-like API and expressions, and to use it I had to pass a lot of parameters when creating the main object. 
However, I wanted to make it very easy to use, like Mecab, and not require users to parse the output themselves. 
So I thought about the API and finally decided to have an API similar to KoNLPy that users are already familiar with.
I believe that these APIs are much more user-friendly and will make the library more easy to use.

## 4. License
Pecab project is licensed under the terms of the **Apache License 2.0**.

```
Copyright 2022 Hyunwoong Ko.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```