package com.example.vpnapp

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.vpnapp.database.PublicKeyItem
import java.util.Base64

class PublicKeyAdapter(
    private var keys: MutableList<PublicKeyItem>, // Mutable list to allow updates
    private val onKeyClick: (PublicKeyItem) -> Unit
) : RecyclerView.Adapter<PublicKeyAdapter.KeyViewHolder>() {

    class KeyViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val keyText: TextView = view.findViewById(R.id.keyTextView)
        val container: View = view.findViewById(R.id.key_text_container)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): KeyViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_public_key, parent, false)
        return KeyViewHolder(view)
    }

    override fun onBindViewHolder(holder: KeyViewHolder, position: Int) {
        val keyItem = keys[position]
        holder.keyText.text = Base64.getEncoder().encodeToString(keyItem.keyPair.public.encoded)

        // Highlight if the key is in use
        holder.container.setBackgroundColor(
            if (keyItem.isInUse) Color.GREEN else Color.TRANSPARENT
        )

        holder.itemView.setOnClickListener {
            onKeyClick(keyItem)
        }
    }

    override fun getItemCount(): Int = keys.size

    // Function to update the list of keys
    fun updateKeys(newKeys: List<PublicKeyItem>) {
        keys.clear()
        keys.addAll(newKeys)
        notifyDataSetChanged() // Notify the adapter that the dataset has changed
    }

    // Optional: Add function to insert an individual item into the list
    fun addKey(keyItem: PublicKeyItem) {
        keys.add(keyItem)
        notifyItemInserted(keys.size - 1) // Notify that a new item was inserted
    }

    // Optional: Function to remove a key item
    fun removeKey(keyItem: PublicKeyItem) {
        val position = keys.indexOf(keyItem)
        if (position != -1) {
            keys.removeAt(position)
            notifyItemRemoved(position) // Notify that an item was removed
        }
    }
}