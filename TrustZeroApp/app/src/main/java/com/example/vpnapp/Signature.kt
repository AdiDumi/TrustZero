package com.example.vpnapp

data class Signature(
    val id: String,         // Unique identifier for the signature (can be app ID or some unique string)
    var signatureText: String, // The signature text itself
    val appIdentifier: String  // Placeholder for app identifier
)