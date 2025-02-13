package com.example.vpnapp

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.example.vpnapp.database.PublicKeyItemDao

class KeyViewModelFactory(private val publicKeyItemDao: PublicKeyItemDao) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        return if (modelClass.isAssignableFrom(KeyViewModel::class.java)) {
            KeyViewModel(publicKeyItemDao) as T
        } else {
            throw IllegalArgumentException("Unknown ViewModel class")
        }
    }
}