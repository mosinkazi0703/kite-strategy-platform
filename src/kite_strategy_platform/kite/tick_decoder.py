import struct
from datetime import datetime, timezone
from kite_strategy_platform.domain.market_data import Quote

def decode_packets(frame: bytes, token_to_contract: dict[int, str], received_at: datetime | None = None):
    if len(frame) < 2: return []
    received_at=received_at or datetime.now(timezone.utc); count=struct.unpack_from(">H",frame,0)[0]; offset=2; result=[]
    for _ in range(count):
        if offset+2>len(frame): break
        length=struct.unpack_from(">H",frame,offset)[0]; offset+=2; packet=frame[offset:offset+length]; offset+=length
        if length<8: continue
        token=struct.unpack_from(">I",packet,0)[0]; ltp=struct.unpack_from(">I",packet,4)[0]/100
        depth=()
        bid=ask=None
        if length>=184:
            depth=tuple({"quantity":struct.unpack_from(">I",packet,off)[0],"price":struct.unpack_from(">I",packet,off+4)[0]/100,"orders":struct.unpack_from(">H",packet,off+8)[0]} for off in range(64,184,12))
            bid=depth[0]["price"] if depth[0]["quantity"] else None
            ask=depth[5]["price"] if depth[5]["quantity"] else None
        if token in token_to_contract: result.append(Quote(token_to_contract[token],received_at,ltp,bid,ask,struct.unpack_from(">I",packet,16)[0] if length>=20 else 0,struct.unpack_from(">I",packet,48)[0] if length>=52 else None,depth))
    return result
