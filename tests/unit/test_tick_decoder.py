import struct
from kite_strategy_platform.kite.tick_decoder import decode_packets
def test_full_packet_reads_depth_not_timestamp_as_bid_ask():
    packet=bytearray(184); struct.pack_into(">I",packet,0,99); struct.pack_into(">I",packet,4,10000); struct.pack_into(">I",packet,16,123); struct.pack_into(">I",packet,48,456)
    struct.pack_into(">IIH",packet,64,10,9900,2); struct.pack_into(">IIH",packet,124,11,10100,3)
    frame=struct.pack(">HH",1,184)+packet; q=decode_packets(frame,{99:"x"})[0]
    assert (q.last,q.bid,q.ask,q.volume,q.open_interest)==(100,99,101,123,456)
