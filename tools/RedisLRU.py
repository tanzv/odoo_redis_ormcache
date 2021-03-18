__all__ = ['RedisLRU']

import pickle
import types


def to_str(obj):
    if isinstance(obj, tuple) or isinstance(obj, list) or isinstance(obj, frozenset) or isinstance(obj, set) \
            or isinstance(obj, enumerate):
        return '[' + ",".join(to_str(i) for i in obj) + ']'
    elif isinstance(obj, dict):
        return '{' + ",".join(to_str(kv) for kv in obj.items()) + '}'
    elif callable(obj):
        return obj.__name__
    else:
        return str(obj)


class RedisLRU(object):

    def __init__(self, redis, namespace, expire):
        self.redis = redis
        self.namespace = namespace
        self.namespace_generation = 0
        self.expire = expire or 604800  # default 7 days in second
        version = self.redis.execute_command("eval ", "return redis.call('get','" + self.namespace + "_generation')", 0)
        if not version:
            self.redis.execute_command("eval ", "return redis.call('incr','" + self.namespace + "_generation')", 0)

    def __contains__(self, obj):
        key = to_str(obj)
        return self.redis.execute_command("eval ",
                                          "return redis.call('exists','" + self.namespace + "_'..redis.call('get','" + self.namespace + "_generation')..'" + key + "')",
                                          0)

    def __getitem__(self, obj):
        key = to_str(obj)
        try:
            res = self.redis.execute_command("eval ",
                                             "return redis.call('get','" + self.namespace + "_'..redis.call('get','" + self.namespace + "_generation')..'" + key + "')",
                                             0)
            if res:
                return pickle.loads(res.encode('latin1'))
        except Exception as e:
            raise TypeError(e)
        raise KeyError("None")

    def __setitem__(self, obj, val):
        if isinstance(val, types.FunctionType):
            self.__delitem__(obj)
            return
        key = to_str(obj)
        jsonval = pickle.dumps(val).decode('latin1')
        self.redis.execute_command("eval ",
                                   "return redis.call('setex','" + self.namespace + "_'..redis.call('get','" + self.namespace + "_generation')..'" +
                                   key + "'," + str(self.expire) + ",KEYS[1])", 1, jsonval)

    def __delitem__(self, obj):
        key = to_str(obj)
        self.redis.execute_command("eval ",
                                   "return redis.call('del','" + self.namespace + "_'..redis.call('get','" + self.namespace + "_generation')..'" + key + "')",
                                   0)

    def get(self, obj):
        return self.__getitem__(obj)

    def set(self, obj, val=None):
        self.__setitem__(obj, val)

    def pop(self, obj):
        res = self.__getitem__(obj)
        self.__delitem__(obj)
        return res

    def clear(self):
        self.redis.execute_command("eval ", "return redis.call('incr','" + self.namespace + "_generation')", 0)
