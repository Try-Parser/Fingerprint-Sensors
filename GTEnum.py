

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

    DETECT_FINGER              = 0x26
    CAPTURE_IMAGE              = 0x60
    MAKE_TEMPLATE              = 0x61
    GET_TEMPLATE               = 0x70
    SET_TEMPLATE               = 0x71
    IDENTIFY_TEMPLATE          = 0xF4
    IDENTIFY_TEMPLATE_PARAM    = 0x1F4

    # Error Response 
    NACK_TIMEOUT               = 0x1001 # (Obsolete) Capture timeout
    NACK_INVALID_BAUDRATE      = 0x1002 # (Obsolete) Invalid serial baud rate
    NACK_INVALID_POS           = 0x1003 # The specified ID is not in range[0,199]
    NACK_IS_NOT_USED           = 0x1004 # The specified ID is not used
    NACK_IS_ALREADY_USED       = 0x1005 # The specified ID is already in use
    NACK_COMM_ERR              = 0x1006 # Communication error
    NACK_VERIFY_FAILED         = 0x1007 # 1:1 Verification Failure
    NACK_IDENTIFY_FAILED       = 0x1008 # 1:N Identification Failure
    NACK_DB_IS_FULL            = 0x1009 # The database is full
    NACK_DB_IS_EMPTY           = 0x100A # The database is empty
    NACK_TURN_ERR              = 0x100B # (Obsolete) Invalid order of the enrollment
                                        # (EnrollStart->Enroll1->Enroll2->Enroll3)
    NACK_BAD_FINGER            = 0x100C # Fingerprint is too bad
    NACK_ENROLL_FAILED         = 0x100D # Enrollment Failure
    NACK_IS_NOT_SUPPORTED      = 0x100E # The command is not supported
    NACK_DEV_ERR               = 0x100F # Device error: probably Crypto-Chip is faulty (Wrong checksum ~Z)
    NACK_CAPTURE_CANCELED      = 0x1010 # (Obsolete) Capturing was canceled
    NACK_INVALID_PARAM         = 0x1011 # nvalid parameter
    NACK_FINGER_IS_NOT_PRESSED = 0x1012 # Finger is not pressed


    COMM_STRUCT                 = lambda: '<BBHIH'
    DATA_STRUCT                 = lambda x: '<BBH' + str(x) + 's'
    CHECK_SUM                   = lambda: '<H'
    ACK                         = 0x30
    NACK                        = 0x31

    CMD_STRT_1                  = 0x55
    CMD_STRT_2                  = 0xAA
    CMD_DATA_1                  = 0x5A
    CMD_DATA_2                  = 0xA5