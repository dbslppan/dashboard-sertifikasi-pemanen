import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import io

# Page configuration
st.set_page_config(
    page_title="Dashboard Sertifikasi Pemanen Kelapa Sawit",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    h1 {
        color: #2e7d32;
        padding-bottom: 10px;
        border-bottom: 3px solid #4caf50;
    }
    h2 {
        color: #1b5e20;
    }
    </style>
    """, unsafe_allow_html=True)

def generate_dummy_data():
    """Generate comprehensive dummy data for oil palm harvesters"""
    np.random.seed(42)
    
    # Worker data
    n_workers = 50
    estates = ['Estate A - Riau', 'Estate B - Jambi', 'Estate C - Sumut', 'Estate D - Kalbar']
    
    data = {
        'ID_Pekerja': [f'HRV{str(i).zfill(4)}' for i in range(1, n_workers + 1)],
        'Nama_Pekerja': [f'Pekerja {i}' for i in range(1, n_workers + 1)],
        'Estate': np.random.choice(estates, n_workers),
        'Tanggal_Sertifikasi': pd.date_range(start='2024-01-15', periods=n_workers, freq='5D'),
        
        # Performance BEFORE certification (baseline lower)
        'Tonase_Sebelum_kg_per_hari': np.random.normal(850, 120, n_workers).round(1),
        'Jumlah_Pokok_Sebelum': np.random.randint(45, 70, n_workers),
        'Brondolan_Loss_Sebelum_pct': np.random.normal(8.5, 2.1, n_workers).round(2),
        'Buah_Mentah_Sebelum_pct': np.random.normal(6.8, 1.8, n_workers).round(2),
        'Buah_Busuk_Sebelum_pct': np.random.normal(4.2, 1.2, n_workers).round(2),
        'Gagang_Panjang_Sebelum_pct': np.random.normal(12.5, 3.2, n_workers).round(2),
        'Hari_Kerja_Sebelum': np.random.randint(22, 26, n_workers),
        
        # Performance AFTER certification (improved)
        'Tonase_Sesudah_kg_per_hari': np.random.normal(1050, 110, n_workers).round(1),
        'Jumlah_Pokok_Sesudah': np.random.randint(60, 85, n_workers),
        'Brondolan_Loss_Sesudah_pct': np.random.normal(4.2, 1.5, n_workers).round(2),
        'Buah_Mentah_Sesudah_pct': np.random.normal(2.8, 1.1, n_workers).round(2),
        'Buah_Busuk_Sesudah_pct': np.random.normal(1.5, 0.8, n_workers).round(2),
        'Gagang_Panjang_Sesudah_pct': np.random.normal(5.2, 1.8, n_workers).round(2),
        'Hari_Kerja_Sesudah': np.random.randint(24, 27, n_workers),
        
        # Financial metrics
        'Upah_Dasar_per_hari': np.random.choice([85000, 90000, 95000], n_workers),
        'Premi_per_kg': np.random.choice([150, 175, 200], n_workers),
        
        # Additional context
        'Lama_Bekerja_tahun': np.random.randint(1, 15, n_workers),
        'Usia': np.random.randint(22, 55, n_workers),
        'Tingkat_Sertifikasi': np.random.choice(['Dasar', 'Madya', 'Mahir'], n_workers, p=[0.5, 0.35, 0.15])
    }
    
    df = pd.DataFrame(data)
    
    # Calculate improvement metrics
    df['Peningkatan_Tonase_pct'] = ((df['Tonase_Sesudah_kg_per_hari'] - df['Tonase_Sebelum_kg_per_hari']) / 
                                     df['Tonase_Sebelum_kg_per_hari'] * 100).round(2)
    df['Peningkatan_Produktivitas_pokok'] = df['Jumlah_Pokok_Sesudah'] - df['Jumlah_Pokok_Sebelum']
    df['Penurunan_Loss_pct'] = (df['Brondolan_Loss_Sebelum_pct'] - df['Brondolan_Loss_Sesudah_pct']).round(2)
    
    # Calculate quality score (0-100)
    df['Kualitas_Score_Sebelum'] = (100 - (
        df['Brondolan_Loss_Sebelum_pct'] * 3 +
        df['Buah_Mentah_Sebelum_pct'] * 4 +
        df['Buah_Busuk_Sebelum_pct'] * 5 +
        df['Gagang_Panjang_Sebelum_pct'] * 2
    )).round(1)
    
    df['Kualitas_Score_Sesudah'] = (100 - (
        df['Brondolan_Loss_Sesudah_pct'] * 3 +
        df['Buah_Mentah_Sesudah_pct'] * 4 +
        df['Buah_Busuk_Sesudah_pct'] * 5 +
        df['Gagang_Panjang_Sesudah_pct'] * 2
    )).round(1)
    
    # Calculate earnings
    df['Pendapatan_Sebelum'] = (df['Upah_Dasar_per_hari'] * df['Hari_Kerja_Sebelum'] + 
                                 df['Tonase_Sebelum_kg_per_hari'] * df['Premi_per_kg'] * df['Hari_Kerja_Sebelum']).round(0)
    df['Pendapatan_Sesudah'] = (df['Upah_Dasar_per_hari'] * df['Hari_Kerja_Sesudah'] + 
                                 df['Tonase_Sesudah_kg_per_hari'] * df['Premi_per_kg'] * df['Hari_Kerja_Sesudah']).round(0)
    df['Peningkatan_Pendapatan'] = (df['Pendapatan_Sesudah'] - df['Pendapatan_Sebelum']).round(0)
    
    return df

def calculate_estate_production(df):
    """Calculate estate-level production metrics"""
    estate_data = []
    
    for estate in df['Estate'].unique():
        estate_df = df[df['Estate'] == estate]
        
        # Calculate total production
        prod_before = (estate_df['Tonase_Sebelum_kg_per_hari'] * estate_df['Hari_Kerja_Sebelum']).sum()
        prod_after = (estate_df['Tonase_Sesudah_kg_per_hari'] * estate_df['Hari_Kerja_Sesudah']).sum()
        
        # Assuming FFB price
        ffb_price = 2800  # Rp per kg
        
        estate_data.append({
            'Estate': estate,
            'Jumlah_Pemanen': len(estate_df),
            'Produksi_Sebelum_ton': prod_before / 1000,
            'Produksi_Sesudah_ton': prod_after / 1000,
            'Peningkatan_ton': (prod_after - prod_before) / 1000,
            'Revenue_Impact_juta': ((prod_after - prod_before) * ffb_price) / 1_000_000,
            'Avg_Quality_Before': estate_df['Kualitas_Score_Sebelum'].mean(),
            'Avg_Quality_After': estate_df['Kualitas_Score_Sesudah'].mean()
        })
    
    return pd.DataFrame(estate_data)

def main():
    st.title("🌴 Dashboard Monitoring Sertifikasi Pemanen Kelapa Sawit")
    st.markdown("**Perkebunan Nusantara - Digital Transformation Team**")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Data")
        uploaded_file = st.file_uploader("Upload CSV Data Pemanen", type=['csv'])
        
        st.markdown("---")
        st.header("⚙️ Filter")
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
        else:
            st.info("Menggunakan data dummy untuk demo")
            df = generate_dummy_data()
            
            # Provide download link for dummy data
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download Template CSV",
                data=csv_buffer.getvalue(),
                file_name="template_data_pemanen.csv",
                mime="text/csv"
            )
        
        # Filters
        selected_estates = st.multiselect(
            "Pilih Estate",
            options=df['Estate'].unique(),
            default=df['Estate'].unique()
        )
        
        selected_certification = st.multiselect(
            "Tingkat Sertifikasi",
            options=df['Tingkat_Sertifikasi'].unique(),
            default=df['Tingkat_Sertifikasi'].unique()
        )
        
        min_improvement = st.slider(
            "Min. Peningkatan Tonase (%)",
            min_value=float(df['Peningkatan_Tonase_pct'].min()),
            max_value=float(df['Peningkatan_Tonase_pct'].max()),
            value=float(df['Peningkatan_Tonase_pct'].min())
        )
    
    # Apply filters
    df_filtered = df[
        (df['Estate'].isin(selected_estates)) &
        (df['Tingkat_Sertifikasi'].isin(selected_certification)) &
        (df['Peningkatan_Tonase_pct'] >= min_improvement)
    ]
    
    # Calculate estate metrics
    estate_metrics = calculate_estate_production(df_filtered)
    
    # ==================== KEY METRICS ====================
    st.header("📊 Ringkasan Performa")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_tonnage_before = df_filtered['Tonase_Sebelum_kg_per_hari'].mean()
        avg_tonnage_after = df_filtered['Tonase_Sesudah_kg_per_hari'].mean()
        improvement = ((avg_tonnage_after - avg_tonnage_before) / avg_tonnage_before * 100)
        st.metric(
            "Rata-rata Tonase Harian",
            f"{avg_tonnage_after:.1f} kg",
            f"+{improvement:.1f}% vs sebelum",
            delta_color="normal"
        )
    
    with col2:
        avg_quality_before = df_filtered['Kualitas_Score_Sebelum'].mean()
        avg_quality_after = df_filtered['Kualitas_Score_Sesudah'].mean()
        quality_improvement = avg_quality_after - avg_quality_before
        st.metric(
            "Skor Kualitas Rata-rata",
            f"{avg_quality_after:.1f}/100",
            f"+{quality_improvement:.1f} poin",
            delta_color="normal"
        )
    
    with col3:
        total_revenue_impact = estate_metrics['Revenue_Impact_juta'].sum()
        st.metric(
            "Dampak Revenue",
            f"Rp {total_revenue_impact:.2f}M",
            "peningkatan produksi",
            delta_color="normal"
        )
    
    with col4:
        avg_income_before = df_filtered['Pendapatan_Sebelum'].mean()
        avg_income_after = df_filtered['Pendapatan_Sesudah'].mean()
        income_improvement = avg_income_after - avg_income_before
        st.metric(
            "Rata-rata Pendapatan",
            f"Rp {avg_income_after/1_000_000:.2f}M",
            f"+Rp {income_improvement/1_000:.0f}K",
            delta_color="normal"
        )
    
    with col5:
        certified_workers = len(df_filtered)
        st.metric(
            "Total Pemanen Tersertifikasi",
            f"{certified_workers}",
            "pekerja aktif"
        )
    
    st.markdown("---")
    
    # ==================== BEFORE vs AFTER COMPARISON ====================
    st.header("📈 Perbandingan Performa: Sebelum vs Sesudah Sertifikasi")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Produktivitas", "⭐ Kualitas Panen", "💰 Dampak Finansial", "🏢 Performa Estate"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Tonase comparison
            fig_tonnage = go.Figure()
            fig_tonnage.add_trace(go.Box(
                y=df_filtered['Tonase_Sebelum_kg_per_hari'],
                name='Sebelum Sertifikasi',
                marker_color='#ff7043'
            ))
            fig_tonnage.add_trace(go.Box(
                y=df_filtered['Tonase_Sesudah_kg_per_hari'],
                name='Sesudah Sertifikasi',
                marker_color='#66bb6a'
            ))
            fig_tonnage.update_layout(
                title='Distribusi Tonase Harian (kg/hari)',
                yaxis_title='Tonase (kg)',
                showlegend=True,
                height=400
            )
            st.plotly_chart(fig_tonnage, use_container_width=True)
        
        with col2:
            # Trees harvested comparison
            fig_trees = go.Figure()
            fig_trees.add_trace(go.Box(
                y=df_filtered['Jumlah_Pokok_Sebelum'],
                name='Sebelum Sertifikasi',
                marker_color='#ff7043'
            ))
            fig_trees.add_trace(go.Box(
                y=df_filtered['Jumlah_Pokok_Sesudah'],
                name='Sesudah Sertifikasi',
                marker_color='#66bb6a'
            ))
            fig_trees.update_layout(
                title='Distribusi Jumlah Pokok Dipanen per Hari',
                yaxis_title='Jumlah Pokok',
                showlegend=True,
                height=400
            )
            st.plotly_chart(fig_trees, use_container_width=True)
        
        # Scatter plot: improvement vs experience
        fig_scatter = px.scatter(
            df_filtered,
            x='Lama_Bekerja_tahun',
            y='Peningkatan_Tonase_pct',
            size='Tonase_Sesudah_kg_per_hari',
            color='Tingkat_Sertifikasi',
            hover_data=['Nama_Pekerja', 'Estate'],
            title='Peningkatan Produktivitas vs Pengalaman Kerja',
            labels={
                'Lama_Bekerja_tahun': 'Lama Bekerja (tahun)',
                'Peningkatan_Tonase_pct': 'Peningkatan Tonase (%)',
                'Tingkat_Sertifikasi': 'Tingkat Sertifikasi'
            },
            color_discrete_map={
                'Dasar': '#42a5f5',
                'Madya': '#ffa726',
                'Mahir': '#ef5350'
            }
        )
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab2:
        # Quality metrics before and after
        quality_metrics = pd.DataFrame({
            'Metrik': ['Brondolan Loss', 'Buah Mentah', 'Buah Busuk', 'Gagang Panjang'],
            'Sebelum': [
                df_filtered['Brondolan_Loss_Sebelum_pct'].mean(),
                df_filtered['Buah_Mentah_Sebelum_pct'].mean(),
                df_filtered['Buah_Busuk_Sebelum_pct'].mean(),
                df_filtered['Gagang_Panjang_Sebelum_pct'].mean()
            ],
            'Sesudah': [
                df_filtered['Brondolan_Loss_Sesudah_pct'].mean(),
                df_filtered['Buah_Mentah_Sesudah_pct'].mean(),
                df_filtered['Buah_Busuk_Sesudah_pct'].mean(),
                df_filtered['Gagang_Panjang_Sesudah_pct'].mean()
            ]
        })
        
        quality_metrics['Penurunan'] = quality_metrics['Sebelum'] - quality_metrics['Sesudah']
        quality_metrics['Penurunan_pct'] = (quality_metrics['Penurunan'] / quality_metrics['Sebelum'] * 100).round(1)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_quality = go.Figure()
            fig_quality.add_trace(go.Bar(
                name='Sebelum',
                x=quality_metrics['Metrik'],
                y=quality_metrics['Sebelum'],
                marker_color='#ff7043'
            ))
            fig_quality.add_trace(go.Bar(
                name='Sesudah',
                x=quality_metrics['Metrik'],
                y=quality_metrics['Sesudah'],
                marker_color='#66bb6a'
            ))
            fig_quality.update_layout(
                title='Perbandingan Metrik Kualitas (%)',
                yaxis_title='Persentase',
                barmode='group',
                height=400
            )
            st.plotly_chart(fig_quality, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Penurunan Defects")
            for idx, row in quality_metrics.iterrows():
                st.metric(
                    row['Metrik'],
                    f"{row['Sesudah']:.1f}%",
                    f"-{row['Penurunan']:.1f}% ({row['Penurunan_pct']:.0f}%)",
                    delta_color="inverse"
                )
        
        # Quality score distribution
        fig_quality_score = go.Figure()
        fig_quality_score.add_trace(go.Histogram(
            x=df_filtered['Kualitas_Score_Sebelum'],
            name='Sebelum Sertifikasi',
            marker_color='#ff7043',
            opacity=0.7,
            nbinsx=20
        ))
        fig_quality_score.add_trace(go.Histogram(
            x=df_filtered['Kualitas_Score_Sesudah'],
            name='Sesudah Sertifikasi',
            marker_color='#66bb6a',
            opacity=0.7,
            nbinsx=20
        ))
        fig_quality_score.update_layout(
            title='Distribusi Skor Kualitas',
            xaxis_title='Skor Kualitas (0-100)',
            yaxis_title='Jumlah Pemanen',
            barmode='overlay',
            height=400
        )
        st.plotly_chart(fig_quality_score, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Income comparison
            fig_income = go.Figure()
            fig_income.add_trace(go.Box(
                y=df_filtered['Pendapatan_Sebelum'] / 1_000_000,
                name='Sebelum Sertifikasi',
                marker_color='#ff7043'
            ))
            fig_income.add_trace(go.Box(
                y=df_filtered['Pendapatan_Sesudah'] / 1_000_000,
                name='Sesudah Sertifikasi',
                marker_color='#66bb6a'
            ))
            fig_income.update_layout(
                title='Distribusi Pendapatan Bulanan',
                yaxis_title='Pendapatan (Juta Rupiah)',
                showlegend=True,
                height=400
            )
            st.plotly_chart(fig_income, use_container_width=True)
        
        with col2:
            # Income improvement by certification level
            income_by_cert = df_filtered.groupby('Tingkat_Sertifikasi').agg({
                'Peningkatan_Pendapatan': 'mean'
            }).reset_index()
            
            fig_cert_income = px.bar(
                income_by_cert,
                x='Tingkat_Sertifikasi',
                y='Peningkatan_Pendapatan',
                title='Rata-rata Peningkatan Pendapatan per Tingkat Sertifikasi',
                labels={
                    'Tingkat_Sertifikasi': 'Tingkat Sertifikasi',
                    'Peningkatan_Pendapatan': 'Peningkatan (Rupiah)'
                },
                color='Tingkat_Sertifikasi',
                color_discrete_map={
                    'Dasar': '#42a5f5',
                    'Madya': '#ffa726',
                    'Mahir': '#ef5350'
                }
            )
            fig_cert_income.update_layout(height=400, showlegend=False)
            fig_cert_income.update_traces(text=income_by_cert['Peningkatan_Pendapatan'].apply(lambda x: f'Rp {x/1000:.0f}K'), textposition='outside')
            st.plotly_chart(fig_cert_income, use_container_width=True)
        
        # Financial breakdown
        st.markdown("### 💵 Breakdown Pendapatan")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_base_salary = df_filtered['Upah_Dasar_per_hari'].mean() * df_filtered['Hari_Kerja_Sesudah'].mean()
            st.metric("Rata-rata Upah Dasar/Bulan", f"Rp {avg_base_salary/1_000_000:.2f}M")
        
        with col2:
            avg_premium_before = (df_filtered['Tonase_Sebelum_kg_per_hari'] * df_filtered['Premi_per_kg'] * df_filtered['Hari_Kerja_Sebelum']).mean()
            avg_premium_after = (df_filtered['Tonase_Sesudah_kg_per_hari'] * df_filtered['Premi_per_kg'] * df_filtered['Hari_Kerja_Sesudah']).mean()
            st.metric("Rata-rata Premi Sebelum", f"Rp {avg_premium_before/1_000_000:.2f}M")
            st.metric("Rata-rata Premi Sesudah", f"Rp {avg_premium_after/1_000_000:.2f}M", f"+Rp {(avg_premium_after - avg_premium_before)/1_000:.0f}K")
        
        with col3:
            total_additional_income = df_filtered['Peningkatan_Pendapatan'].sum()
            st.metric("Total Tambahan Pendapatan", f"Rp {total_additional_income/1_000_000:.2f}M", "untuk semua pemanen")
    
    with tab4:
        # Estate performance
        st.markdown("### 🏢 Performa per Estate")
        
        fig_estate = go.Figure()
        fig_estate.add_trace(go.Bar(
            name='Produksi Sebelum',
            x=estate_metrics['Estate'],
            y=estate_metrics['Produksi_Sebelum_ton'],
            marker_color='#ff7043'
        ))
        fig_estate.add_trace(go.Bar(
            name='Produksi Sesudah',
            x=estate_metrics['Estate'],
            y=estate_metrics['Produksi_Sesudah_ton'],
            marker_color='#66bb6a'
        ))
        fig_estate.update_layout(
            title='Total Produksi per Estate (Ton)',
            yaxis_title='Produksi (Ton)',
            barmode='group',
            height=400
        )
        st.plotly_chart(fig_estate, use_container_width=True)
        
        # Estate metrics table
        estate_metrics_display = estate_metrics.copy()
        estate_metrics_display['Produksi_Sebelum_ton'] = estate_metrics_display['Produksi_Sebelum_ton'].round(2)
        estate_metrics_display['Produksi_Sesudah_ton'] = estate_metrics_display['Produksi_Sesudah_ton'].round(2)
        estate_metrics_display['Peningkatan_ton'] = estate_metrics_display['Peningkatan_ton'].round(2)
        estate_metrics_display['Revenue_Impact_juta'] = estate_metrics_display['Revenue_Impact_juta'].round(2)
        estate_metrics_display['Avg_Quality_Before'] = estate_metrics_display['Avg_Quality_Before'].round(1)
        estate_metrics_display['Avg_Quality_After'] = estate_metrics_display['Avg_Quality_After'].round(1)
        
        st.dataframe(
            estate_metrics_display.style.format({
                'Produksi_Sebelum_ton': '{:.2f}',
                'Produksi_Sesudah_ton': '{:.2f}',
                'Peningkatan_ton': '{:.2f}',
                'Revenue_Impact_juta': 'Rp {:.2f}M',
                'Avg_Quality_Before': '{:.1f}',
                'Avg_Quality_After': '{:.1f}'
            }),
            use_container_width=True,
            height=250
        )
    
    st.markdown("---")
    
    # ==================== TOP PERFORMERS ====================
    st.header("🏆 Top Performers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Top 10 Peningkatan Produktivitas")
        top_productivity = df_filtered.nlargest(10, 'Peningkatan_Tonase_pct')[
            ['Nama_Pekerja', 'Estate', 'Tonase_Sebelum_kg_per_hari', 'Tonase_Sesudah_kg_per_hari', 'Peningkatan_Tonase_pct']
        ].reset_index(drop=True)
        top_productivity.index += 1
        st.dataframe(top_productivity, use_container_width=True, height=400)
    
    with col2:
        st.markdown("### ⭐ Top 10 Kualitas Tertinggi")
        top_quality = df_filtered.nlargest(10, 'Kualitas_Score_Sesudah')[
            ['Nama_Pekerja', 'Estate', 'Kualitas_Score_Sebelum', 'Kualitas_Score_Sesudah', 'Tingkat_Sertifikasi']
        ].reset_index(drop=True)
        top_quality.index += 1
        st.dataframe(top_quality, use_container_width=True, height=400)
    
    st.markdown("---")
    
    # ==================== DETAILED DATA TABLE ====================
    st.header("📋 Data Lengkap Pemanen")
    
    # Select columns to display
    display_columns = [
        'ID_Pekerja', 'Nama_Pekerja', 'Estate', 'Tingkat_Sertifikasi',
        'Tonase_Sebelum_kg_per_hari', 'Tonase_Sesudah_kg_per_hari', 'Peningkatan_Tonase_pct',
        'Kualitas_Score_Sebelum', 'Kualitas_Score_Sesudah',
        'Pendapatan_Sebelum', 'Pendapatan_Sesudah', 'Peningkatan_Pendapatan'
    ]
    
    st.dataframe(
        df_filtered[display_columns].style.format({
            'Tonase_Sebelum_kg_per_hari': '{:.1f}',
            'Tonase_Sesudah_kg_per_hari': '{:.1f}',
            'Peningkatan_Tonase_pct': '{:.2f}%',
            'Kualitas_Score_Sebelum': '{:.1f}',
            'Kualitas_Score_Sesudah': '{:.1f}',
            'Pendapatan_Sebelum': 'Rp {:,.0f}',
            'Pendapatan_Sesudah': 'Rp {:,.0f}',
            'Peningkatan_Pendapatan': 'Rp {:,.0f}'
        }),
        use_container_width=True,
        height=400
    )
    
    # Download button for filtered data
    csv_output = io.StringIO()
    df_filtered.to_csv(csv_output, index=False)
    st.download_button(
        label="📥 Download Data Terfilter (CSV)",
        data=csv_output.getvalue(),
        file_name=f"data_pemanen_tersertifikasi_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # ==================== INSIGHTS & RECOMMENDATIONS ====================
    st.markdown("---")
    st.header("💡 Insight & Rekomendasi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Key Findings")
        avg_improvement = df_filtered['Peningkatan_Tonase_pct'].mean()
        avg_quality_imp = df_filtered['Kualitas_Score_Sesudah'].mean() - df_filtered['Kualitas_Score_Sebelum'].mean()
        
        st.success(f"""
        **Dampak Sertifikasi Positif:**
        - Peningkatan produktivitas rata-rata: **{avg_improvement:.1f}%**
        - Peningkatan skor kualitas: **+{avg_quality_imp:.1f} poin**
        - Penurunan brondolan loss: **{(df_filtered['Brondolan_Loss_Sebelum_pct'].mean() - df_filtered['Brondolan_Loss_Sesudah_pct'].mean()):.1f}%**
        - Tambahan pendapatan pemanen: **Rp {df_filtered['Peningkatan_Pendapatan'].mean()/1000:.0f}K/bulan**
        """)
        
        if len(df_filtered) > 0:
            best_estate = estate_metrics.nlargest(1, 'Revenue_Impact_juta')['Estate'].values[0]
            st.info(f"""
            **Estate Terbaik:** {best_estate}
            - Menunjukkan peningkatan revenue tertinggi
            - Model best practice untuk estate lain
            """)
    
    with col2:
        st.markdown("### 🎯 Rekomendasi Strategis")
        
        # Identify areas for improvement
        low_performers = df_filtered[df_filtered['Peningkatan_Tonase_pct'] < df_filtered['Peningkatan_Tonase_pct'].quantile(0.25)]
        
        st.warning(f"""
        **Area Perbaikan:**
        - {len(low_performers)} pemanen perlu pendampingan tambahan
        - Fokus pada pemanen dengan tingkat sertifikasi Dasar
        - Implementasi mentoring dari top performers
        """)
        
        st.info("""
        **Langkah Selanjutnya:**
        1. Scale up program sertifikasi ke seluruh estate
        2. Refreshment training untuk pemanen lama
        3. Sistem insentif berbasis kualitas
        4. Monitoring berkala performa pasca-sertifikasi
        """)

if __name__ == "__main__":
    main()
