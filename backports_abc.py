try:
    import collections.abc as _collections_abc
except ImportError:
    import collections as _collections_abc


def mk_gen():
    from abc import abstractmethod

    required_methods = (
        '__iter__', '__next__' if hasattr(iter(()), '__next__') else 'next',
         'send', 'throw', 'close')

    class Generator(_collections_abc.Iterator):
        __slots__ = ()

        if '__next__' in required_methods:
            def __next__(self):
                return self.send(None)
        else:
            def next(self):
                return self.send(None)

        @abstractmethod
        def send(self, value):
            raise StopIteration

        @abstractmethod
        def throw(self, typ, val=None, tb=None):
            if val is None:
                if tb is None:
                    raise typ
                val = typ()
            if tb is not None:
                val = val.with_traceback(tb)
            raise val

        def close(self):
            try:
                self.throw(GeneratorExit)
            except (GeneratorExit, StopIteration):
                pass
            else:
                raise RuntimeError('generator ignored GeneratorExit')

        @classmethod
        def __subclasshook__(cls, C):
            if cls is Generator:
                mro = C.__mro__
                for method in required_methods:
                    for base in mro:
                        if method in base.__dict__:
                            break
                    else:
                        return NotImplemented
                return True
            return NotImplemented

    generator = type((lambda: (yield))())
    Generator.register(generator)
    return Generator

try:
    Generator = _collections_abc.Generator
except AttributeError:
    Generator = _collections_abc.Generator = mk_gen()


def mk_awaitable():
    from abc import abstractmethod, ABCMeta

    @abstractmethod
    def __await__(self):
        yield

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Awaitable:
            for B in C.__mro__:
                if '__await__' in B.__dict__:
                    if B.__dict__['__await__']:
                        return True
                    break
        return NotImplemented

    # calling metaclass directly as syntax differs in Py2/Py3
    Awaitable = ABCMeta('Awaitable', (), {
        '__slots__': (),
        '__await__': __await__,
        '__subclasshook__': __subclasshook__,
    })

    return Awaitable

try:
    Awaitable = _collections_abc.Awaitable
except AttributeError:
    Awaitable = _collections_abc.Awaitable = mk_awaitable()


try:
    from inspect import isawaitable
except ImportError:
    def isawaitable(obj):
        return isinstance(obj, _collections_abc.Awaitable)
    import inspect
    inspect.isawaitable = isawaitable


def mk_coroutine():
    from abc import abstractmethod, ABCMeta

    class Coroutine(Awaitable):
        __slots__ = ()

        @abstractmethod
        def send(self, value):
            """Send a value into the coroutine.
            Return next yielded value or raise StopIteration.
            """
            raise StopIteration

        @abstractmethod
        def throw(self, typ, val=None, tb=None):
            """Raise an exception in the coroutine.
            Return next yielded value or raise StopIteration.
            """
            if val is None:
                if tb is None:
                    raise typ
                val = typ()
            if tb is not None:
                val = val.with_traceback(tb)
            raise val

        def close(self):
            """Raise GeneratorExit inside coroutine.
            """
            try:
                self.throw(GeneratorExit)
            except (GeneratorExit, StopIteration):
                pass
            else:
                raise RuntimeError('coroutine ignored GeneratorExit')

        @classmethod
        def __subclasshook__(cls, C):
            if cls is Coroutine:
                mro = C.__mro__
                for method in ('__await__', 'send', 'throw', 'close'):
                    for base in mro:
                        if method in base.__dict__:
                            break
                    else:
                        return NotImplemented
                return True
            return NotImplemented

    return Coroutine

try:
    Coroutine = _collections_abc.Coroutine
except AttributeError:
    Coroutine = _collections_abc.Coroutine = mk_coroutine()


try:
    from inspect import iscoroutine
except ImportError:
    def iscoroutine(obj):
        return isinstance(obj, _collections_abc.Coroutine)
    import inspect
    inspect.iscoroutine = iscoroutine