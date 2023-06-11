using Guna.UI2.WinForms.Suite;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Xml.Linq;

namespace WindowsFormsApp1
{
    public partial class Form2 : Form
    {
        public bool isDone = false;
        public Form2()
        {
            InitializeComponent();
        }

        private void guna2Button2_Click(object sender, EventArgs e)
        {
            isDone = false;
            Close();
        }

        private async void guna2Button1_Click(object sender, EventArgs e)
        {
            ProductAdd product = new ProductAdd
            {
                name = guna2TextBox1.Text,
                category = guna2TextBox2.Text,
                price = guna2TextBox3.Text,
                description = guna2TextBox4.Text
            };

            string json = JsonConvert.SerializeObject(product);
            HttpClient client = new HttpClient();
            string targetUrl = "http://127.0.0.1:8000";
            client.BaseAddress = new Uri(targetUrl);
            HttpContent content = new StringContent(json, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await client.PostAsync("addProduct", content);
            isDone = true;
            Close();

        }
    }
    public class ProductAdd
    {
        public string name { get; set; }
        public string category { get; set; }
        public string price { get; set; }
        public string description { get; set; }
    }
}
