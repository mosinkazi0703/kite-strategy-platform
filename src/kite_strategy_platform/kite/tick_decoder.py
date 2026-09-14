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
        if length>=44:
            bid=struct.unpack_from(">I",packet,44)[0]/100 if length>=48 else None
            ask=struct.unpack_from(">I",packet,56)[0]/100 if length>=60 else None
        else: bid=ask=None
        if token in token_to_contract: result.append(Quote(token_to_contract[token],received_at,ltp,bid,ask,struct.unpack_from(">I",packet,20)[0] if length>=24 else 0,struct.unpack_from(">I",packet,48)[0] if length>=52 else None))
    return result
