import discord
from const import DEBUG, SERVER_ID, SERVER_ID_TEST


SERVER = SERVER_ID_TEST if DEBUG else SERVER_ID


class PSIDModal(discord.ui.Modal, title='PSID 登録フォーム'):
    psid = discord.ui.TextInput(label='PSIDを入力してください')

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.client.get_guild(SERVER)

        if guild:
            member = guild.get_member(interaction.user.id)

            if member:
                try:
                    await member.edit(nick=self.psid.value)
                    await interaction.response.send_message(
                        f'PSID `{self.psid.value}` を登録しました！',
                        ephemeral=True
                    )
                except discord.Forbidden:
                    await interaction.response.send_message(
                        '登録に失敗しました🤦‍♀️'
                    )
            
            else:
                print('on_submit: Could not find member info in the server.')
        
        else:
            print('on_submit: Could not find the server')


class RegisterView(discord.ui.View):
    @discord.ui.button(label='PSIDを入力', style=discord.ButtonStyle.primary)
    async def register(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(PSIDModal())
