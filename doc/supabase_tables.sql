-- Supabase表创建脚本
-- 请在Supabase控制台的SQL编辑器中执行此脚本

-- 创建users表
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- 创建requirements表
CREATE TABLE IF NOT EXISTS public.requirements (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    creator_id INTEGER NOT NULL REFERENCES public.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'draft'
);

-- 创建user_requirements表（多对多关系表）
CREATE TABLE IF NOT EXISTS public.user_requirements (
    user_id INTEGER REFERENCES public.users(id),
    requirement_id VARCHAR(36) REFERENCES public.requirements(id),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    role VARCHAR(50) DEFAULT 'member',
    PRIMARY KEY (user_id, requirement_id)
);

-- 创建requirement_contents表
CREATE TABLE IF NOT EXISTS public.requirement_contents (
    id SERIAL PRIMARY KEY,
    requirement_id VARCHAR(36) NOT NULL REFERENCES public.requirements(id),
    content_type VARCHAR(50),
    content_text TEXT,
    file_path VARCHAR(255),
    submitted_by INTEGER NOT NULL REFERENCES public.users(id),
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为requirements表添加更新时间触发器
DROP TRIGGER IF EXISTS update_requirements_updated_at ON public.requirements;
CREATE TRIGGER update_requirements_updated_at
    BEFORE UPDATE ON public.requirements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 启用行级安全性（RLS）
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.requirement_contents ENABLE ROW LEVEL SECURITY;

-- 创建基本的RLS策略（允许所有操作，后续可以根据需要调整）
CREATE POLICY "Allow all operations on users" ON public.users FOR ALL USING (true);
CREATE POLICY "Allow all operations on requirements" ON public.requirements FOR ALL USING (true);
CREATE POLICY "Allow all operations on user_requirements" ON public.user_requirements FOR ALL USING (true);
CREATE POLICY "Allow all operations on requirement_contents" ON public.requirement_contents FOR ALL USING (true);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_users_username ON public.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_requirements_creator_id ON public.requirements(creator_id);
CREATE INDEX IF NOT EXISTS idx_requirements_status ON public.requirements(status);
CREATE INDEX IF NOT EXISTS idx_requirement_contents_requirement_id ON public.requirement_contents(requirement_id);
CREATE INDEX IF NOT EXISTS idx_requirement_contents_submitted_by ON public.requirement_contents(submitted_by);

-- 插入测试数据（可选）
INSERT INTO public.users (username, email, password_hash) VALUES 
('admin', 'admin@example.com', '9e79654c6526b2976064f8bf5351a6bde642bb15325736edc0b692a44bd9faf3') 
ON CONFLICT (username) DO NOTHING;

COMMIT;