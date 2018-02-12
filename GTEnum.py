

"""
Command Packet:
OFFSET  ITEM        TYPE    DESCRIPTION
----------------------------------------------------------------
0       0x55        BYTE    Command start code 1
1       0xAA        BYTE    Command start code 2
2       Device ID   WORD    Device ID (default: 0x0001)
4       Parameter   DWORD   Input parameter
8       Command     WORD    Command code
10      Checksum    WORD    Byte addition checksum

Response Packet:
OFFSET  ITEM        TYPE    DESCRIPTION
----------------------------------------------------------------
0       0x55        BYTE    Response code 1
1       0xAA        BYTE    Response code 2
2       Device ID   WORD    Device ID (default: 0x0001)
4       Parameter   DWORD   Error code
8       Response    WORD    Response (ACK/NACK)
10      Checksum    WORD    Byte addition checksum

Data Packet:
OFFSET  ITEM        TYPE    DESCRIPTION
----------------------------------------------------------------
0       0x5A        BYTE    Data code 1
1       0xA5        BYTE    Data code 2
2       Device ID   WORD    Device ID (default: 0x0001)
4       Parameter   N BYTES N bytes of data - size predefined
4 + N   Checksum    WORD    Byte addition checksum
"""
from enum import Enum

class GT521F5(Enum):
    # Command
    DEFAULT                    = 0x00
    OPEN                       = 0x01
    CLOSE                      = 0x02
    USB_INTERNAL_CHECK         = 0x03
    SET_BAUDRATE               = 0x04
    SET_AIP_MODE               = 0x05
    CMOS_LED                   = 0x12

    GET_ENROLL_COUNT           = 0x20
    CHECK_ENROLLED             = 0x21
    START_ENROLL               = 0x22
    FIRST_ENROLL               = 0x23
    SECOND_ENROLL              = 0x24
    THIRD_MATCH_SAVE           = 0x25

    DELETE_FP_ID               = 0x40
    DELETE_FP_ALL              = 0x41

    VERIFICATION               = 0x50
    IDENTIFICATION             = 0x51

    DETECT_FINGER              = 0x26
    CAPTURE_IMAGE              = 0x60
    MAKE_TEMPLATE              = 0x61
    GET_TEMPLATE               = 0x70
    SET_TEMPLATE               = 0x71
    IDENTIFY_TEMPLATE          = 0xF4
    IDENTIFY_TEMPLATE_PARAM    = 0x1F4

    ERRORS = {
        # Error Response 
        0x1001: 'NACK_TIMEOUT',               # (Obsolete) Capture timeout
        0x1002: 'NACK_INVALID_BAUDRATE',      # (Obsolete) Invalid serial baud rate
        0x1003: 'NACK_INVALID_POS',           # The specified ID is not in range[0,199]
        0x1004: 'NACK_IS_NOT_USED',           # The specified ID is not used
        0x1005: 'NACK_IS_ALREADY_USED',       # The specified ID is already in use
        0x1006: 'NACK_COMM_ERR',              # Communication error
        0x1007: 'NACK_VERIFY_FAILED',         # 1:1 Verification Failure
        0x1008: 'NACK_IDENTIFY_FAILED',       # 1:N Identification Failure
        0x1009: 'NACK_DB_IS_FULL',            # The database is full
        0x100A: 'NACK_DB_IS_EMPTY',           # The database is empty
        0x100B: 'NACK_TURN_ERR',              # (Obsolete) Invalid order of the enrollment
                                             # (EnrollStart->Enroll1->Enroll2->Enroll3)
        0x100C: 'NACK_BAD_FINGER',            # Fingerprint is too bad
        0x100D: 'NACK_ENROLL_FAILED',         # Enrollment Failure
        0x100E: 'NACK_IS_NOT_SUPPORTED',      # The command is not supported
        0x100F: 'NACK_DEV_ERR',               # Device error: probably Crypto-Chip is faulty (Wrong checksum ~Z)
        0x1010: 'NACK_CAPTURE_CANCELED',      # (Obsolete) Capturing was canceled
        0x1011: 'NACK_INVALID_PARAM',         # nvalid parameter
        0x1012: 'NACK_FINGER_IS_NOT_PRESSED' # Finger is not pressed
    }

    COMM_STRUCT                 = lambda: '<BBHIH'
    DATA_STRUCT                 = lambda x: '<BBH' + str(x) + 's'
    CHECK_SUM_STRUCT            = lambda: '<H'
    ACK                         = 0x30
    NACK                        = 0x31

    CMD_STRT_1                  = 0x55
    CMD_STRT_2                  = 0xAA
    CMD_DATA_1                  = 0x5A
    CMD_DATA_2                  = 0xA5