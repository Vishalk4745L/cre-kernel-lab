type Props = {
  title: string;
  description: string;
};

export function PageHeader({ title, description }: Props) {
  return (
    <header className="page-header">
      <h2>{title}</h2>
      <p>{description}</p>
    </header>
  );
}
