package com.example.vpnapp

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.ViewModel
import com.example.vpnapp.database.PublicKeyItem
import com.example.vpnapp.database.PublicKeyItemDao
import com.google.gson.Gson
import kotlinx.coroutines.launch

class KeyViewModel(private val publicKeyItemDao: PublicKeyItemDao) : ViewModel() {

    // Use LiveData to observe the keys
    private val _keys = MutableLiveData<List<PublicKeyItem>>()
    val keys: LiveData<List<PublicKeyItem>> get() = _keys

    fun getAllKeys() = viewModelScope.launch {
        val result = publicKeyItemDao.getAllKeys() // suspend function that fetches data
        _keys.postValue(result) // Use postValue to update LiveData from a background thread
    }

    fun insertPublicKeyItem(item: PublicKeyItem) = viewModelScope.launch {
        publicKeyItemDao.insert(item)
        getAllKeys() // Refresh keys after insertion
    }

    fun updatePublicKeyItem(item: PublicKeyItem) = viewModelScope.launch {
        publicKeyItemDao.update(item)
        getAllKeys() // Refresh keys after update
    }

    fun deletePublicKeyItem(item: PublicKeyItem) = viewModelScope.launch {
        publicKeyItemDao.delete(item)
        getAllKeys() // Refresh keys after deletion
    }

    fun updateSignatures(keyId: Long, newSignatures: MutableList<Signature>) = viewModelScope.launch {
        val jsonSignatures = Gson().toJson(newSignatures)
        publicKeyItemDao.updateSignatures(keyId, jsonSignatures)
    }
}

