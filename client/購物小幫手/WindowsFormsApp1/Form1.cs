using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Security.Policy;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Runtime.InteropServices;
using System.Diagnostics;
using Newtonsoft.Json; // Nuget Package
using static System.Windows.Forms.VisualStyles.VisualStyleElement;

namespace WindowsFormsApp1
{

    public partial class Form1 : Form
    {
        public const int WM_NCLBUTTONDOWN = 0xA1;
        public const int HT_CAPTION = 0x2;
        [System.Runtime.InteropServices.DllImport("user32.dll")]
        public static extern int SendMessage(IntPtr hWnd, int Msg, int wParam, int lParam);
        [System.Runtime.InteropServices.DllImport("user32.dll")]
        public static extern bool ReleaseCapture();
        public Form1()
        {
            InitializeComponent();
            getData();
            Debug.WriteLine("App started");
            this.FormBorderStyle = FormBorderStyle.None;
            tabControl1.Appearance = TabAppearance.FlatButtons;
            tabControl1.ItemSize = new Size(0, 1);
            tabControl1.SizeMode = TabSizeMode.Fixed;
            tabControl2.Appearance = TabAppearance.FlatButtons;
            tabControl2.ItemSize = new Size(0, 1);
            tabControl2.SizeMode = TabSizeMode.Fixed;


        }

        private void flowLayoutPanel2_MouseDown(object sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left)
            {
                ReleaseCapture();
                SendMessage(Handle, WM_NCLBUTTONDOWN, HT_CAPTION, 0);
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            Application.Exit();
        }

        private void flowLayoutPanel2_Paint(object sender, PaintEventArgs e)
        {

        }

        private void button1_Click(object sender, EventArgs e)
        {
            tabControl1.SelectedTab = tabControl1.TabPages[1];
        }

        private void button3_Click(object sender, EventArgs e)
        {
            tabControl1.SelectedTab = tabControl1.TabPages[2];
        }
        private void button4_Click(object sender, EventArgs e)
        {
            tabControl1.SelectedTab = tabControl1.TabPages[3];
        }
        private void label1_Click(object sender, EventArgs e)
        {
            tabControl1.SelectedTab = tabControl1.TabPages[0];
        }

        private void button5_Click(object sender, EventArgs e)
        {
            // switch max the window or not
            if (this.WindowState == FormWindowState.Maximized)
            {
                this.WindowState = FormWindowState.Normal;
                button5.Text = "🗖";
            }
            else
            {
                this.WindowState = FormWindowState.Maximized;
                button5.Text = "🗗";
            }
            
        }

        private void ChatSend1_Click(object sender, EventArgs e)
        {


        }

        private void guna2GradientButton2_Click(object sender, EventArgs e)
        {
            tabControl2.SelectedIndex = 0;
        }

        private void guna2GradientButton1_Click(object sender, EventArgs e)
        {
            tabControl2.SelectedIndex = 1;
        }

        private void Form1_Load(object sender, EventArgs e)
        {

        }

        private async void getData()
        {
            // 訪問API 127.0.0.1:8000/getProducts
            string targetUrl = "http://127.0.0.1:8000";
            HttpClient client = new HttpClient();
            client.BaseAddress = new Uri(targetUrl);
            client.DefaultRequestHeaders.Accept.Add(
            new MediaTypeWithQualityHeaderValue("application/json"));
            HttpResponseMessage response = client.GetAsync("getProducts").Result;

            if (response.IsSuccessStatusCode)
            {
                Debug.WriteLine(response.ToString());
            }
            string jsonStr = await response.Content.ReadAsStringAsync();


            var result = JsonConvert.DeserializeObject<ResponseData>(jsonStr);

            List<Product> productList = result.msg;

            foreach (var product in productList)
            {
                // 假设每个商品信息包含 id、name、category、price 和 fileName 字段
                string id = product.id.ToString();
                string name = product.name.ToString();
                string category = product.category.ToString();
                string price = product.price.ToString();
                string fileName = product.fileName.ToString();

                // 创建包含商品信息的 ListViewItem 对象
                ListViewItem item = new ListViewItem(new[] { id, name, category, price, fileName });

                // 将 ListViewItem 添加到 listView1 控件中
                listView1.Items.Add(item);
            }

        }

        private void guna2Button5_Click(object sender, EventArgs e)
        {
            listView1.Items.Clear();
            getData();
        }

        private void guna2Button1_Click(object sender, EventArgs e)
        {
            Form2 guna = new Form2();
            guna.ShowDialog();
            if (guna.isDone)
            {
                listView1.Items.Clear();
                getData();
            }

        }

        private async void guna2Button2_Click(object sender, EventArgs e)
        {
            HttpClient client = new HttpClient();
            string targetUrl = "http://127.0.0.1:8000";
            client.BaseAddress = new Uri(targetUrl);
            HttpResponseMessage response = await client.GetAsync("reload_data");

            if (response.StatusCode == HttpStatusCode.OK)
            {
                MessageBox.Show("向量資料庫建構成功!");
            }
        }

        private async void 提問_Click(object sender, EventArgs e)
        {
            Question question = new Question();
            question.question = ChatTextBox1.Text;
            string json = JsonConvert.SerializeObject(question);
            HttpClient client = new HttpClient();
            string targetUrl = "http://127.0.0.1:8000";
            client.BaseAddress = new Uri(targetUrl);
            HttpContent content = new StringContent(json, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await client.PostAsync("chat_withProduct", content);
            string res = await response.Content.ReadAsStringAsync();
            string trimmedJson = res.Trim('"');
            string formattedJson = trimmedJson.Replace("\\n", Environment.NewLine);
            guna2TextBox1.Text = formattedJson;
        }
    }
    public class ResponseData
    {
        public List<Product> msg { get; set; }
    }

    public class Product
    {
        public string id { get; set; }
        public string name { get; set; }
        public string category { get; set; }
        public string price { get; set; }
        public string fileName { get; set; }
    }
    public class Question
    {
        public string question { get; set; }
    }
}
