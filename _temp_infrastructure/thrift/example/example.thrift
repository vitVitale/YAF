namespace cpp com.baeldung.thrift.impl
namespace java com.baeldung.thrift.impl

enum Operation {
  GOOD = 0,
  ERROR = 1
}

struct TCheckTokenRq {
    1: required string token;
    2: string operUid;
}

struct CrossPlatformResource {
    1: i32 id,
    2: string name,
    3: optional string salutation,
    4: required Operation op,
    5: required TCheckTokenRq token_rq,
}

exception InvalidOperationException {
    1: i32 code,
    2: string description
}

service CrossPlatformService {

    CrossPlatformResource get(1:i32 id) throws (1:InvalidOperationException e),

    void save(1:CrossPlatformResource resource, 2:list <TCheckTokenRq> list_token_rqs) throws (1:InvalidOperationException e),

    list <CrossPlatformResource> getList() throws (1:InvalidOperationException e),

    bool ping() throws (1:InvalidOperationException e)
}