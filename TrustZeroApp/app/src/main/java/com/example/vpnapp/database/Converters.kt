package com.example.vpnapp.database

import androidx.room.TypeConverter
import java.security.KeyPair
import java.security.KeyFactory
import java.security.spec.PKCS8EncodedKeySpec
import java.security.spec.X509EncodedKeySpec
import java.util.Base64

class Converters {

    @TypeConverter
    fun fromKeyPair(keyPair: KeyPair): String {
        val publicKey = Base64.getEncoder().encodeToString(keyPair.public.encoded)
        val privateKey = Base64.getEncoder().encodeToString(keyPair.private.encoded)
        return "$publicKey,$privateKey"
    }

    @TypeConverter
    fun toKeyPair(keyPairString: String): KeyPair {
        val (publicKeyString, privateKeyString) = keyPairString.split(",")
        val keyFactory = KeyFactory.getInstance("RSA")

        val publicKey = KeyFactory.getInstance("RSA").generatePublic(
            X509EncodedKeySpec(Base64.getDecoder().decode(publicKeyString))
        )

        val privateKey = KeyFactory.getInstance("RSA").generatePrivate(
            PKCS8EncodedKeySpec(Base64.getDecoder().decode(privateKeyString))
        )

        return KeyPair(publicKey, privateKey)
    }
}
