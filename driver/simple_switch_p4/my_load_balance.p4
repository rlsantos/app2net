/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<4>  res;
    bit<1>  cwr;
    bit<1>  ece;
    bit<1>  urg;
    bit<1>  ack;
    bit<1>  psh;
    bit<1>  rst;
    bit<1>  syn;
    bit<1>  fin;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}


struct metadata {
    bit<32> rng;
    bit<16> tcpLength;
}

struct headers {
    ethernet_t ethernet;
    ipv4_t     ipv4;
    tcp_t      tcp;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {
    state start {
        transition parse_ethernet;
    }
    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            0x800: parse_ipv4;
            default: accept;
        }
    }
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        meta.tcpLength = hdr.ipv4.totalLen - 16w20;
        transition select(hdr.ipv4.protocol) {
            8w6: parse_tcp;
            default: accept;
        }
    }
    state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    bit<1> direction = 0;
    register< bit<32> >(4096) live_connection;
    register< bit<32> >(4096) send_to;
 
    action set_rng_meta(bit<32> num_buckets) {
        random(meta.rng, 1, num_buckets);
    }
    
    table set_dst_server {
        key = {}
        actions = {
            set_rng_meta;
            NoAction;
        }
        size = 1;
        default_action = NoAction;
    }

    action set_direction(bit<1> direc) {
        direction = direc;
    }

    table check_direction{
        key = {
            hdr.ipv4.srcAddr: exact;
        }

        actions = {
            set_direction;
            NoAction;
        }
        size = 1024;
        default_action = NoAction;
    }

    action ipv4_forward(bit<48> dstAddr, bit<9> port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action to_internal_ipv4_forward(bit<48> dstAddr, bit<9> port, bit<32> ipv4dstAddr) {
        ipv4_forward(dstAddr, port);
        hdr.ipv4.dstAddr = ipv4dstAddr;
    }

    action to_external_ipv4_forward(bit<48> dstAddr, bit<9> port, bit<32> vipv4) {
        ipv4_forward(dstAddr, port);
        hdr.ipv4.srcAddr = vipv4;
    }

    action drop() {
        mark_to_drop(standard_metadata);
    }


    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
            meta.rng: exact;
        }
        actions = {
            to_internal_ipv4_forward;
            to_external_ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    apply {
        if (hdr.ipv4.isValid()){
            bit<32> idx;
            bit<32> waiting;
            bit<32> live;

            set_dst_server.apply();
            check_direction.apply();
            
            if (direction == 0) {
                hash(idx, HashAlgorithm.crc16, (bit<32>) 0, {hdr.ipv4.srcAddr}, (bit<32>)4096);
                live_connection.read(live, idx);
                if (live == 1) {
                    send_to.read(meta.rng, idx);

                    if (hdr.tcp.fin == 1) {
                        live_connection.write(idx, 0);
                        send_to.write(idx, 0);
                    }
                } else {
                    if (hdr.tcp.syn == 1) {
                        live_connection.write(idx, 1);
                        send_to.write(idx, meta.rng);
                    }
                }
            } else {
                meta.rng = 0;
                hash(idx, HashAlgorithm.crc16, (bit<32>)0, {hdr.ipv4.dstAddr}, (bit<32>)4096);
            }

            ipv4_lpm.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    
    apply { }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply { 
        update_checksum(
            hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
        update_checksum_with_payload(
            hdr.ipv4.isValid() && hdr.tcp.isValid(),
            {
                hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr,
                8w0,
                hdr.ipv4.protocol,
                meta.tcpLength,
                hdr.tcp.srcPort,
                hdr.tcp.dstPort,
                hdr.tcp.seqNo,
                hdr.tcp.ackNo,
                hdr.tcp.dataOffset,
                hdr.tcp.res,
                hdr.tcp.cwr,
                hdr.tcp.ece,
                hdr.tcp.urg,
                hdr.tcp.ack,
                hdr.tcp.psh,
                hdr.tcp.rst,
                hdr.tcp.syn,
                hdr.tcp.fin,
                hdr.tcp.window,
                hdr.tcp.urgentPtr
            },
            hdr.tcp.checksum,
            HashAlgorithm.csum16
        );
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply { 
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.tcp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
