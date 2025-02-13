package com.example.vpnapp.database

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.Query
import androidx.room.Update

@Dao
interface PublicKeyItemDao {

    @Insert
    suspend fun insert(publicKeyItem: PublicKeyItem)

    @Update
    suspend fun update(publicKeyItem: PublicKeyItem)

    @Query("UPDATE public_key_items SET signatures = :signaturesJson WHERE id = :keyId")
    suspend fun updateSignatures(keyId: Long, signaturesJson: String)

    @Delete
    suspend fun delete(publicKeyItem: PublicKeyItem)

    @Query("SELECT * FROM public_key_items")
    suspend fun getAllKeys(): List<PublicKeyItem>
}
