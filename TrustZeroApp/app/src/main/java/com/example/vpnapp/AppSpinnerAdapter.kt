package com.example.vpnapp

import android.content.Context
import android.graphics.drawable.Drawable
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.ImageView
import android.widget.TextView

class AppSpinnerAdapter(context: Context, private val appList: List<AppInfo>) :
    ArrayAdapter<AppInfo>(context, 0, appList) {

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        return createViewFromResource(position, convertView, parent)
    }

    override fun getDropDownView(position: Int, convertView: View?, parent: ViewGroup): View {
        return createViewFromResource(position, convertView, parent)
    }

    private fun createViewFromResource(position: Int, convertView: View?, parent: ViewGroup): View {
        val view = convertView ?: LayoutInflater.from(context).inflate(R.layout.item_app_spinner, parent, false)

        val appIcon = view.findViewById<ImageView>(R.id.appIcon)
        val appName = view.findViewById<TextView>(R.id.appName)

        val app = appList[position]
        appIcon.setImageDrawable(app.icon)
        appName.text = app.name

        return view
    }
}