package com.example.vpnapp

import android.content.Intent
import android.net.VpnService
import android.os.ParcelFileDescriptor
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import java.io.FileInputStream
import java.io.FileOutputStream
import java.io.IOException
import java.net.Socket

class MyVpnService : VpnService() {

    private var vpnInterface: ParcelFileDescriptor? = null
    private var selectedAppPackage: String? = null
    private lateinit var vpnInputStream: FileInputStream
    private lateinit var vpnOutputStream: FileOutputStream

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Retrieve the package name passed from MainActivity
        selectedAppPackage = intent?.getStringExtra("selectedAppPackage")

        // Log or check if the package name was received correctly
        Log.d("MyVpnService", "Selected App Package: $selectedAppPackage")

        // Start VPN setup based on the selected app
        if (selectedAppPackage != null) {
            startVpn(selectedAppPackage!!)
            vpnInputStream = FileInputStream(vpnInterface?.fileDescriptor)
            vpnOutputStream = FileOutputStream(vpnInterface?.fileDescriptor)
            // Start a separate thread to handle the VPN traffic in the background
            Thread {
                handleTraffic()
            }.start()
        }

        return START_STICKY
    }

    private fun startVpn(packageName: String) {
        val builder = Builder()

        // Set up the VPN session name
        builder.setSession("My VPN Service")

        builder.addAddress("10.0.0.2", 32)
        builder.addRoute("0.0.0.0", 0)
        builder.addAllowedApplication(packageName) // Restrict to one app
        vpnInterface = builder.establish()
        if (vpnInterface == null) {
            Log.e("MyVpnService", "Failed to establish VPN interface")
            return
        }

        Log.d("MyVpnService", "VPN established for app: $packageName")
    }

    private fun handleTraffic() {
        val buffer = ByteArray(32767)

        while (true) {
            val length = vpnInputStream.read(buffer)
            if (length > 0) {
                val rawData = buffer.copyOfRange(0, length)

                val ipPacket = IpPacket(rawData)

                when {
                    ipPacket.isTcp -> {
                        val destinationPort = ipPacket.getDestinationPort()
                        val destinationIP = ipPacket.destinationIP
                        forwardPacket(destinationIP, destinationPort, ipPacket.getTcpSegmentToForward())
                    }
                    ipPacket.isUdp -> {
                        val destinationPort = ipPacket.getDestinationPort()
                        val destinationIP = ipPacket.destinationIP
                        forwardPacket(destinationIP, destinationPort, ipPacket.getUdpSegmentToForward())
                    }
                    ipPacket.isIcmp -> {
                        val destinationIP = ipPacket.destinationIP
                        forwardPacket(destinationIP, ipPacket.getIcmpSegmentToForward())
                    }
                   ipPacket.isIgmp -> {
                        val destinationIP = ipPacket.destinationIP
                        forwardPacket(destinationIP, ipPacket.getIcmpSegmentToForward())
                    }
                    else -> {
                        Log.e("VPN", "Unsupported protocol")
                        // Optionally forward unrecognized protocols
                        val destinationIP = ipPacket.destinationIP
                        forwardPacket(destinationIP, rawData)
                    }
                }

//                // Check IP version
//                val version = (data[0].toUByte().toInt() and 0xF0) shr 4
//                var destinationIP = ""
//                var destinationPort = 0
//                when (version) {
//                    4 -> { // Handle IPv4
//                        // Extract IP header fields
//                        val protocol = data[9].toUByte().toInt() and 0xFF
//                        val sourceIP = "${data[12].toUByte().toInt() and 0xFF}.${data[13].toUByte().toInt() and 0xFF}.${data[14].toUByte().toInt() and 0xFF}.${data[15].toUByte().toInt() and 0xFF}"
//                        destinationIP = "${data[16].toUByte().toInt() and 0xFF}.${data[17].toUByte().toInt() and 0xFF}.${data[18].toUByte().toInt() and 0xFF}.${data[19].toUByte().toInt() and 0xFF}"
//
//                        // Extract Total Length (16 bits)
//                        val totalLength = ((data[2].toUByte().toInt() and 0xFF) shl 8) or (data[3].toUByte().toInt() and 0xFF)
//
//                        // Extract Identification (16 bits)
//                        val identification = ((data[4].toUByte().toInt() and 0xFF) shl 8) or (data[5].toUByte().toInt() and 0xFF)
//
//                        // Extract TTL (8 bits)
//                        val ttl = data[8].toUByte().toInt() and 0xFF
//
//                        // Extract Flags (3 bits) and Fragment Offset (13 bits)
//                        val flags = (data[6].toUByte().toInt() and 0xE0) shr 5
//                        val fragmentOffset = ((data[6].toUByte().toInt() and 0x1F) shl 8) or (data[7].toUByte().toInt() and 0xFF)
//
//                        // Extract Header Checksum (16 bits)
//                        val checksum = ((data[10].toUByte().toInt() and 0xFF) shl 8) or (data[11].toUByte().toInt() and 0xFF)
//
//                        // Calculate IP header length (IHL)
//                        val ipHeaderLength = (data[0].toUByte().toInt() and 0x0F) * 4
//
//                        // Print IP header details
//                        Log.d("VPN Traffic", "IPv4 Packet")
//                        Log.d("VPN Traffic", "Protocol: $protocol")
//                        Log.d("VPN Traffic", "Source IP: $sourceIP, Destination IP: $destinationIP")
//                        Log.d("VPN Traffic", "Total Length: $totalLength bytes")
//                        Log.d("VPN Traffic", "Identification: $identification")
//                        Log.d("VPN Traffic", "TTL: $ttl")
//                        Log.d("VPN Traffic", "Flags: $flags, Fragment Offset: $fragmentOffset")
//                        Log.d("VPN Traffic", "Header Checksum: $checksum")
//
//                        // Now extract the payload (the data after the IP header)
//                        val payloadStart = ipHeaderLength
//                        val payload = data.copyOfRange(payloadStart, data.size)
//
//                        // If it's TCP or UDP, we can further extract the transport header and payload
//                        if (protocol == 6) { // TCP Protocol
//                            Log.d("VPN Traffic", "This is a TCP packet")
//                            val tcpPayload = extractTcpPayload(payload)
//                            Log.d("VPN Traffic", "TCP Payload: ${tcpPayload?.let { String(it) }}")
//                        } else if (protocol == 17) { // UDP Protocol
//                            Log.d("VPN Traffic", "This is a UDP packet")
//                            val udpPayload = extractUdpPayload(payload)
//                            Log.d("VPN Traffic", "UDP Payload: ${udpPayload?.let { String(it) }}")
//                        } else {
//                            Log.d("VPN Traffic", "This is not a TCP or UDP packet. Payload might not be transport data.")
//                        }
//
//                        // Extract Source Port (2 bytes)
//                        val sourcePort = ((payload[0].toUByte().toInt() shl 8) or (payload[1].toUByte()
//                            .toInt() and 0xFF))
//
//                        // Extract Destination Port (2 bytes)
//                        destinationPort = ((payload[2].toUByte().toInt() shl 8) or (payload[3].toUByte()
//                            .toInt() and 0xFF))
//
//                        // Extract Sequence Number (4 bytes)
//                        val sequenceNumber = ((payload[4].toUByte().toInt() shl 24) or (payload[5].toUByte()
//                            .toInt() shl 16) or
//                                (payload[6].toUByte().toInt() shl 8) or (payload[7].toUByte()
//                            .toInt()))
//
//                        // Extract Acknowledgment Number (4 bytes)
//                        val acknowledgmentNumber = ((payload[8].toUByte().toInt() shl 24) or (payload[9].toUByte()
//                            .toInt() shl 16) or
//                                (payload[10].toUByte().toInt() shl 8) or (payload[11].toUByte()
//                            .toInt()))
//
//                        // Extract Data Offset (Header Length) and Flags
//                        val dataOffsetAndFlags = payload[12].toUByte().toInt()
//                        val dataOffset = (dataOffsetAndFlags shr 4) * 4  // Data offset (in 32-bit words, multiply by 4 to get bytes)
//                        val flags2 = payload[13].toUByte().toInt()
//
//                        // Extract Window Size (2 bytes)
//                        val windowSize = ((payload[14].toUByte().toInt() shl 8) or (payload[15].toUByte()
//                            .toInt()))
//
//                        // Extract Checksum (2 bytes)
//                        val checksum2 = ((payload[16].toUByte().toInt() shl 8) or (payload[17].toUByte()
//                            .toInt()))
//
//                        // Extract Urgent Pointer (2 bytes)
//                        val urgentPointer = ((payload[18].toUByte().toInt() shl 8) or (payload[19].toUByte()
//                            .toInt()))
//
//                        // Print parsed values
//                        Log.d("TCP Header", "Source Port: $sourcePort")
//                        Log.d("TCP Header", "Destination Port: $destinationPort")
//                        Log.d("TCP Header", "Sequence Number: $sequenceNumber")
//                        Log.d("TCP Header", "Acknowledgment Number: $acknowledgmentNumber")
//                        Log.d("TCP Header", "Data Offset: $dataOffset bytes")
//                        Log.d("TCP Header", "Flags: $flags2 (binary: ${flags.toString(2)})")
//                        Log.d("TCP Header", "Window Size: $windowSize")
//                        Log.d("TCP Header", "Checksum: $checksum2")
//                        Log.d("TCP Header", "Urgent Pointer: $urgentPointer")
//                        // Optional: Log the raw payload
//                        Log.d("VPN Traffic", data.joinToString(" ") { it.toString(16).padStart(2, '0') })
//                    }
//                }
//                if (destinationIP != "" && destinationPort != 0) {
//                    GlobalScope.launch(Dispatchers.IO) {
//                        try {
//                            // Perform network operations in the background
//                            val socket = Socket(destinationIP, destinationPort)
//                            socket.getOutputStream().write(data)
//                            // Read the server's response
//                            val response = socket.getInputStream().readBytes()
//
//                            Log.d("VPN", "Response to be written: ${response.size} bytes")
//                            // Forward the response back to the VPN Output Stream
//                            if (response.isNotEmpty()) {
//                                vpnOutputStream.write(response)
//                            } else {
//                                Log.e("VPN", "Response is empty, cannot write to vpnOutputStream")
//                            }
//                            vpnOutputStream.write(response)
//
//                            // Close the socket after the transaction
//                            socket.close()
//                        } catch (e: IOException) {
//                            e.printStackTrace() // Handle any exceptions like network issues
//                        }
//                    }
//                    Log.d("VPN Sending", "SendData to $destinationIP and $destinationPort")
//                }
            }
        }
    }

    private fun forwardPacket(destinationIP: String, destinationPort: Int?, data: ByteArray?) {
        if (data == null) {
            return
        }

        try {
            val socket = Socket(destinationIP, destinationPort!!)
            val outputStream = socket.getOutputStream()
            val inputStream = socket.getInputStream()

            // Send the TCP data to the destination
            outputStream.write(data)
            outputStream.flush()

            // Read response from the destination
            val responseBuffer = ByteArray(1024)
            val bytesRead = inputStream.read(responseBuffer)
            if (bytesRead > 0) {
                // Send the response back through the VPN
                vpnOutputStream.write(responseBuffer, 0, bytesRead)
            }

            socket.close()
        } catch (e: IOException) {
            Log.e("VPN", "Error forwarding packet: ${e.message}")
        }
    }

    private fun forwardPacket(destinationIP: String, icmpSegment: ByteArray?) {
        // Handle ICMP forwarding separately
        if (icmpSegment == null) {
            return
        }

        try {
            // Forward the ICMP packet (no destination port for ICMP)
            val socket = Socket(destinationIP, 0) // ICMP does not use ports

            socket.getOutputStream().write(icmpSegment)

            socket.close()
        } catch (e: IOException) {
            Log.e("VPN", "Error forwarding ICMP packet: ${e.message}")
        }
    }

//    // Function to extract TCP Payload (assuming standard TCP header length)
//    fun extractTcpPayload(tcpSegment: ByteArray): ByteArray? {
//        val tcpHeaderLength = (tcpSegment[12].toUByte().toInt() shr 4) * 4
//        return if (tcpHeaderLength < tcpSegment.size) {
//            tcpSegment.copyOfRange(tcpHeaderLength, tcpSegment.size)
//        } else {
//            null
//        }
//    }
//
//    // Function to extract UDP Payload
//    fun extractUdpPayload(udpSegment: ByteArray): ByteArray? {
//        // UDP header is fixed at 8 bytes
//        return if (udpSegment.size > 8) {
//            udpSegment.copyOfRange(8, udpSegment.size)
//        } else {
//            null
//        }
//    }
//
//    private fun handlePacket(buffer: ByteBuffer): ByteBuffer {
//        // Extract raw bytes from the ByteBuffer
//        val rawBytes = ByteArray(buffer.remaining())
//        buffer.get(rawBytes)
//
//        var returnPacket = buffer
//        // Parse as an IP packet
//        val ipPacket = IpPacket(rawBytes)
//        val str = ipPacket.rawBytes[9].toUByte().toInt()
//        val hd = (ipPacket.rawBytes[0].toUByte().toInt() and 0x0F) * 4
//        Log.d("MyVpnService", "IpPacket is $str and $hd")
//        if (ipPacket.isTcp) {
//            val tcpSegment = ipPacket.getTcpSegment() ?: return returnPacket
//            val tcpPacket = TcpPacket(tcpSegment)
//
//            // Check if this is an HTTP request
//            if (tcpPacket.isHttpRequest()) {
//                returnPacket = modifyHttpPacket(tcpPacket, ipPacket)
//                Log.d("MyVpnService", "TcpPacket is : $returnPacket")
//            }
//        }
//
//        return returnPacket
//    }
//
//    private fun modifyHttpPacket(tcpPacket: TcpPacket, ipPacket: IpPacket): ByteBuffer {
//        val originalPayload = tcpPacket.payload()
//
//        // Add the custom header to the HTTP payload
//        val modifiedPayload = addCustomHeader(originalPayload)
//
//        // Rebuild the TCP packet with the modified payload
//        val modifiedTcpPacket = tcpPacket.rebuildWithPayload(modifiedPayload)
//
//        // Combine the modified TCP packet with the original IP header
//        val modifiedIpPacket = ByteBuffer.allocate(ipPacket.rawBytes.size).apply {
//            put(ipPacket.rawBytes, 0, ipPacket.ipHeaderLength) // Copy IP header
//            put(modifiedTcpPacket) // Add modified TCP payload
//        }
//
//        return modifiedIpPacket
//    }
//
//    private fun TcpPacket.isHttpRequest(): Boolean {
//        val payload = this.payload()
//        return payload.startsWith("GET") || payload.startsWith("POST") || payload.startsWith("HEAD")
//    }
//
//    private fun addCustomHeader(originalPayload: String): String {
//        // Custom header to add
//        val customHeader = "X-Custom-Header: MyHeaderValue\r\n"
//
//        // Find the end of the HTTP headers (marked by \r\n\r\n)
//        val headerEndIndex = originalPayload.indexOf("\r\n\r\n")
//        if (headerEndIndex == -1) return originalPayload // Not a valid HTTP request
//
//        // Insert the custom header
//        val modifiedPayload = StringBuilder(originalPayload)
//            .insert(headerEndIndex + 2, customHeader) // +2 to insert after the last \r\n
//            .toString()
//
//        return modifiedPayload
//    }


    override fun onDestroy() {
        super.onDestroy()
        vpnInterface?.close()
        Log.d("MyVpnService", "VPN Service is being destroyed")
        stopSelf()
    }

}

class IpPacket(private val rawBytes: ByteArray) {
    private val ipHeaderLength: Int
        get() = (rawBytes[0].toUByte().toInt() and 0x0F) * 4 // IHL (Internet Header Length)

    val isTcp: Boolean
        get() = (rawBytes[9].toUByte().toInt() == 6) // Protocol field: 6 for TCP

    val isUdp: Boolean
        get() = (rawBytes[9].toUByte().toInt() == 17) // Protocol field: 17 for UDP

    val isIcmp: Boolean
        get() = (rawBytes[9].toUByte().toInt() == 1) // Protocol field: 1 for ICMP

    val isIgmp: Boolean
        get() = (rawBytes[9].toUByte().toInt() == 2) // Protocol field: 2 for IGMP

    val destinationIP: String
        get() {
            return "${rawBytes[16].toUByte().toInt()}.${rawBytes[17].toUByte().toInt()}." +
                    "${rawBytes[18].toUByte().toInt()}.${rawBytes[19].toUByte().toInt()}"
        }

    fun getDestinationPort(): Int? {
        if (!isTcp) return null

        // Calculate the starting point of the TCP header after the IP header
        val tcpHeaderStart = ipHeaderLength
        if (rawBytes.size < tcpHeaderStart + 4) { // Ensure at least 4 bytes for Source Port and Destination Port
            return null
        }

        // Extract the Destination Port (bytes 2 and 3 of the TCP header)
        val destinationPort = (rawBytes[tcpHeaderStart + 2].toUByte().toInt() shl 8) or (rawBytes[tcpHeaderStart + 3].toUByte().toInt())

        return destinationPort
    }

    fun getTcpSegmentToForward(): ByteArray? {
        if (!isTcp) return null

        // Calculate the starting point of the TCP header after the IP header
        val tcpHeaderStart = ipHeaderLength
        if (rawBytes.size < tcpHeaderStart + 20) { // Minimum TCP header size is 20 bytes
            return null
        }

        // Get the Data Offset (TCP header length in 32-bit words)
        val dataOffset = (rawBytes[tcpHeaderStart + 12].toUByte().toInt() shr 4)
        val tcpHeaderLength = dataOffset * 4

        if (rawBytes.size < tcpHeaderStart + tcpHeaderLength) {
            return null // Invalid TCP header length
        }

        // Return the raw TCP data (header + payload)
        return rawBytes.copyOfRange(tcpHeaderStart, rawBytes.size)
    }

    fun getUdpSegmentToForward(): ByteArray? {
        if (!isUdp) return null

        // Calculate the starting point of the UDP header after the IP header
        val udpHeaderStart = ipHeaderLength
        if (rawBytes.size < udpHeaderStart + 8) { // Minimum UDP header size is 8 bytes
            return null
        }

        // Return the raw UDP data (header + payload)
        return rawBytes.copyOfRange(udpHeaderStart, rawBytes.size)
    }

    fun getIcmpSegmentToForward(): ByteArray? {
        if (!isIcmp) return null

        // Calculate the starting point of the ICMP header after the IP header
        val icmpHeaderStart = ipHeaderLength
        if (rawBytes.size < icmpHeaderStart + 4) { // Minimum ICMP header size is 4 bytes
            return null
        }

        // Return the raw ICMP data (header + payload)
        return rawBytes.copyOfRange(icmpHeaderStart, rawBytes.size)
    }

}
