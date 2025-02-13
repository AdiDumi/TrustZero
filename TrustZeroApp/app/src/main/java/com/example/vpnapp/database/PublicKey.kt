package com.example.vpnapp.database

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.example.vpnapp.Signature
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.security.KeyPair

@Entity(tableName = "public_key_items")
data class PublicKeyItem(
    @PrimaryKey(autoGenerate = true) val id: Long = 0L,
    val keyPair: KeyPair, // Store serialized KeyPair
    var signatures: String = "[]", // Store serialized signatures as JSON
    var isInUse: Boolean = false // Track if this key is currently "in use"
) {
    // Convert JSON string to MutableList<Signature>
    fun getSignaturesList(): MutableList<Signature> {
        return Gson().fromJson(signatures, object : TypeToken<MutableList<Signature>>() {}.type) ?: mutableListOf()
    }

    // Convert MutableList<Signature> back to JSON string
    fun updateSignatures(newSignatures: MutableList<Signature>) {
        this.signatures = Gson().toJson(newSignatures)
    }
}